#!/usr/bin/env python3
"""
APK Reverse Engineering - Script de Análise Automática
Usa androguard para análise estática completa de APKs Android.
"""

import sys
import os
import hashlib
import zipfile
import json
import re
from pathlib import Path

# --- Permissões consideradas perigosas / interessantes ---
DANGEROUS_PERMS = {
    "android.permission.READ_SMS",
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.READ_CALL_LOG",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.GET_ACCOUNTS",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.INSTALL_PACKAGES",
    "android.permission.DELETE_PACKAGES",
    "android.permission.BIND_DEVICE_ADMIN",
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.REQUEST_INSTALL_PACKAGES",
}

# Padrões de strings suspeitas
SUSPICIOUS_PATTERNS = [
    (r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "URL com IP direto"),
    (
        r"(?i)(api[_\-]?key|apikey|secret[_\-]?key|access[_\-]?token)",
        "Possível chave de API",
    ),
    (r"(?i)(password|passwd|pwd)\s*[=:]\s*\S+", "Possível senha hardcoded"),
    (r"(?i)(c2|command.?and.?control|beacon)", "Terminologia C2"),
    (r"(?i)(root|superuser|su\b)", "Referência a root"),
    (r"(?i)(base64|encode|decode|cipher|encrypt|decrypt)", "Operação de codificação"),
    (r'https?://[^\s"\'<>]+', "URL externa"),
]

# APIs Android sensíveis (classe -> métodos)
SENSITIVE_APIS = {
    "Landroid/telephony/SmsManager;": ["sendTextMessage", "sendMultipartTextMessage"],
    "Landroid/telephony/TelephonyManager;": [
        "getDeviceId",
        "getSubscriberId",
        "getLine1Number",
    ],
    "Landroid/location/LocationManager;": [
        "getLastKnownLocation",
        "requestLocationUpdates",
    ],
    "Ljava/net/URL;": ["openConnection"],
    "Landroid/content/ContentResolver;": ["query"],
    "Landroid/hardware/Camera;": ["open"],
    "Landroid/media/MediaRecorder;": ["setAudioSource"],
    "Ljava/lang/Runtime;": ["exec"],
    "Landroid/app/admin/DevicePolicyManager;": ["lockNow", "wipeData"],
}


def file_hashes(path: str) -> dict:
    data = Path(path).read_bytes()
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "size_mb": round(len(data) / 1024 / 1024, 2),
    }


def list_zip_contents(apk_path: str) -> dict:
    """Lista arquivos dentro do APK (que é um ZIP)."""
    result = {
        "files": [],
        "has_multiple_dex": False,
        "has_native_libs": False,
        "assets": [],
    }
    try:
        with zipfile.ZipFile(apk_path) as z:
            names = z.namelist()
            result["files"] = names
            dex_count = sum(1 for n in names if n.endswith(".dex"))
            result["has_multiple_dex"] = dex_count > 1
            result["dex_count"] = dex_count
            result["has_native_libs"] = any(n.endswith(".so") for n in names)
            result["native_libs"] = [n for n in names if n.endswith(".so")]
            result["assets"] = [n for n in names if n.startswith("assets/")]
    except Exception as e:
        result["error"] = str(e)
    return result


def analyze_with_androguard(apk_path: str) -> dict:
    """Análise principal usando androguard."""
    try:
        from androguard.misc import AnalyzeAPK
    except ImportError:
        return {
            "error": "androguard não instalado. Execute: pip install androguard --break-system-packages"
        }

    result = {}
    print("[*] Carregando APK com androguard (pode demorar para APKs grandes)...")

    try:
        a, d, dx = AnalyzeAPK(apk_path)
    except Exception as e:
        return {"error": f"Falha ao analisar APK: {e}"}

    # --- Metadados ---
    result["metadata"] = {
        "package": a.get_package(),
        "app_name": a.get_app_name(),
        "version_name": a.get_androidversion_name(),
        "version_code": a.get_androidversion_code(),
        "min_sdk": a.get_min_sdk_version(),
        "target_sdk": a.get_target_sdk_version(),
        "main_activity": a.get_main_activity(),
    }

    # --- Permissões ---
    all_perms = a.get_permissions()
    dangerous = [p for p in all_perms if p in DANGEROUS_PERMS]
    result["permissions"] = {
        "all": all_perms,
        "dangerous": dangerous,
        "total_count": len(all_perms),
        "dangerous_count": len(dangerous),
    }

    # --- Componentes ---
    result["components"] = {
        "activities": a.get_activities(),
        "services": a.get_services(),
        "receivers": a.get_receivers(),
        "providers": a.get_providers(),
    }

    # --- Strings interessantes ---
    print("[*] Extraindo strings...")
    urls = []
    suspicious_strings = []
    all_strings_sample = []

    for s_obj in dx.get_strings():
        s = s_obj.get_orig_value()
        if len(s) < 4 or len(s) > 500:
            continue
        if len(all_strings_sample) < 200:
            all_strings_sample.append(s)
        # Detectar URLs
        if re.search(r"https?://", s):
            urls.append(s.strip())
        # Detectar padrões suspeitos
        for pattern, label in SUSPICIOUS_PATTERNS:
            if re.search(pattern, s):
                suspicious_strings.append({"string": s.strip(), "reason": label})
                break

    result["strings"] = {
        "urls": list(set(urls))[:50],
        "suspicious": suspicious_strings[:30],
        "sample": all_strings_sample[:50],
    }

    # --- Classes ---
    print("[*] Analisando classes...")
    classes = list(dx.get_classes())
    class_names = [c.name for c in classes]

    # Detectar ofuscação (classes com nomes curtos tipo a, b, c)
    short_names = [
        n
        for n in class_names
        if len(n.replace("/", "").replace(";", "").replace("L", "")) <= 3
    ]
    obfuscation_ratio = len(short_names) / max(len(class_names), 1)

    result["classes"] = {
        "total": len(class_names),
        "obfuscation_suspected": obfuscation_ratio > 0.3,
        "obfuscation_ratio": round(obfuscation_ratio, 2),
        "sample": class_names[:30],
        "interesting": [
            n
            for n in class_names
            if any(
                kw in n.lower()
                for kw in [
                    "crypt",
                    "network",
                    "http",
                    "socket",
                    "root",
                    "hide",
                    "reflect",
                ]
            )
        ][:20],
    }

    # --- APIs Sensíveis ---
    print("[*] Buscando chamadas de API sensíveis...")
    found_apis = {}
    for method in dx.get_methods():
        for _, call, _ in method.get_xref_to():
            cls = call.class_name
            name = call.name
            if cls in SENSITIVE_APIS and name in SENSITIVE_APIS[cls]:
                key = f"{cls}->{name}"
                if key not in found_apis:
                    found_apis[key] = 0
                found_apis[key] += 1

    result["sensitive_apis"] = found_apis

    # --- Certificado ---
    try:
        certs = a.get_certificates()
        result["certificates"] = []
        for cert in certs:
            result["certificates"].append(
                {
                    "subject": str(cert.subject),
                    "issuer": str(cert.issuer),
                    "serial": str(cert.serial_number),
                    "not_before": (
                        str(cert.not_valid_before_utc)
                        if hasattr(cert, "not_valid_before_utc")
                        else "N/A"
                    ),
                    "not_after": (
                        str(cert.not_valid_after_utc)
                        if hasattr(cert, "not_valid_after_utc")
                        else "N/A"
                    ),
                }
            )
    except Exception as e:
        result["certificates"] = [{"error": str(e)}]

    return result


def format_report(apk_path: str, hashes: dict, zip_info: dict, analysis: dict) -> str:
    """Formata o relatório final em texto legível."""
    lines = []
    sep = "=" * 60

    lines.append(sep)
    lines.append(f"  RELATÓRIO DE ENGENHARIA REVERSA - APK")
    lines.append(f"  Arquivo: {Path(apk_path).name}")
    lines.append(sep)

    # Hashes
    lines.append("\n📁 INFORMAÇÕES DO ARQUIVO")
    lines.append(f"  Tamanho: {hashes['size_mb']} MB ({hashes['size_bytes']:,} bytes)")
    lines.append(f"  MD5:     {hashes['md5']}")
    lines.append(f"  SHA1:    {hashes['sha1']}")
    lines.append(f"  SHA256:  {hashes['sha256']}")

    if "error" in analysis:
        lines.append(f"\n❌ ERRO NA ANÁLISE: {analysis['error']}")
        return "\n".join(lines)

    # Metadados
    m = analysis.get("metadata", {})
    lines.append("\n📱 METADADOS DO APP")
    lines.append(f"  Pacote:         {m.get('package', 'N/A')}")
    lines.append(f"  Nome:           {m.get('app_name', 'N/A')}")
    lines.append(
        f"  Versão:         {m.get('version_name', 'N/A')} (code: {m.get('version_code', 'N/A')})"
    )
    lines.append(f"  SDK mínimo:     {m.get('min_sdk', 'N/A')}")
    lines.append(f"  SDK alvo:       {m.get('target_sdk', 'N/A')}")
    lines.append(f"  Activity main:  {m.get('main_activity', 'N/A')}")

    # Estrutura ZIP
    lines.append("\n🗂️  ESTRUTURA DO APK")
    lines.append(
        f"  Arquivos DEX: {zip_info.get('dex_count', 'N/A')} {'⚠️ múltiplos DEX' if zip_info.get('has_multiple_dex') else ''}"
    )
    lines.append(
        f"  Libs nativas: {'✅ SIM' if zip_info.get('has_native_libs') else 'Não'}"
    )
    if zip_info.get("native_libs"):
        for lib in zip_info["native_libs"][:5]:
            lines.append(f"    - {lib}")
    lines.append(f"  Assets: {len(zip_info.get('assets', []))} arquivo(s)")

    # Permissões
    p = analysis.get("permissions", {})
    lines.append(
        f"\n🔐 PERMISSÕES ({p.get('total_count', 0)} total, {p.get('dangerous_count', 0)} perigosas)"
    )
    if p.get("dangerous"):
        lines.append("  ⚠️  PERMISSÕES PERIGOSAS:")
        for perm in p["dangerous"]:
            lines.append(f"    🔴 {perm}")
    other_perms = [p2 for p2 in p.get("all", []) if p2 not in DANGEROUS_PERMS]
    if other_perms:
        lines.append("  Outras permissões:")
        for perm in other_perms[:10]:
            lines.append(f"    - {perm}")
        if len(other_perms) > 10:
            lines.append(f"    ... e mais {len(other_perms) - 10}")

    # Componentes
    comp = analysis.get("components", {})
    lines.append("\n🧩 COMPONENTES ANDROID")
    lines.append(f"  Activities ({len(comp.get('activities', []))}):")
    for act in comp.get("activities", [])[:5]:
        lines.append(f"    - {act}")
    lines.append(f"  Services ({len(comp.get('services', []))}):")
    for svc in comp.get("services", [])[:5]:
        lines.append(f"    - {svc}")
    lines.append(f"  Receivers ({len(comp.get('receivers', []))}):")
    for rcv in comp.get("receivers", [])[:5]:
        lines.append(f"    - {rcv}")

    # Classes
    cls = analysis.get("classes", {})
    lines.append(f"\n☕ CLASSES ({cls.get('total', 0)} total)")
    if cls.get("obfuscation_suspected"):
        lines.append(
            f"  ⚠️  OFUSCAÇÃO DETECTADA (ratio: {cls.get('obfuscation_ratio', 0):.0%})"
        )
    if cls.get("interesting"):
        lines.append("  Classes de interesse:")
        for c in cls["interesting"][:10]:
            lines.append(f"    - {c}")

    # APIs Sensíveis
    apis = analysis.get("sensitive_apis", {})
    if apis:
        lines.append(f"\n⚡ CHAMADAS DE API SENSÍVEIS ({len(apis)})")
        for api, count in list(apis.items())[:15]:
            lines.append(f"  🔴 {api} (chamado {count}x)")

    # URLs
    strings = analysis.get("strings", {})
    urls = strings.get("urls", [])
    if urls:
        lines.append(f"\n🌐 URLs ENCONTRADAS ({len(urls)})")
        for url in urls[:15]:
            lines.append(f"  - {url}")

    # Strings suspeitas
    susp = strings.get("suspicious", [])
    if susp:
        lines.append(f"\n🚨 STRINGS SUSPEITAS ({len(susp)})")
        for item in susp[:10]:
            lines.append(f"  [{item['reason']}] {item['string'][:100]}")

    # Certificados
    certs = analysis.get("certificates", [])
    if certs:
        lines.append(f"\n🔏 CERTIFICADOS ({len(certs)})")
        for cert in certs:
            if "error" not in cert:
                lines.append(f"  Subject: {cert.get('subject', 'N/A')}")
                lines.append(f"  Issuer:  {cert.get('issuer', 'N/A')}")
                lines.append(f"  Serial:  {cert.get('serial', 'N/A')}")
                lines.append(
                    f"  Válido:  {cert.get('not_before', 'N/A')} → {cert.get('not_after', 'N/A')}"
                )

    lines.append(f"\n{sep}")
    lines.append("  FIM DO RELATÓRIO")
    lines.append(sep)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analyze_apk.py <caminho_do_apk>")
        print("Exemplo: python3 analyze_apk.py /mnt/user-data/uploads/app.apk")
        sys.exit(1)

    apk_path = sys.argv[1]
    if not os.path.exists(apk_path):
        print(f"Erro: Arquivo não encontrado: {apk_path}")
        sys.exit(1)

    output_json = "--json" in sys.argv

    print(f"[*] Analisando: {apk_path}")

    hashes = file_hashes(apk_path)
    print(f"[*] Hash SHA256: {hashes['sha256']}")

    zip_info = list_zip_contents(apk_path)
    print(f"[*] Arquivos no APK: {len(zip_info.get('files', []))}")

    analysis = analyze_with_androguard(apk_path)

    if output_json:
        result = {"hashes": hashes, "zip": zip_info, "analysis": analysis}
        print(json.dumps(result, indent=2, default=str))
    else:
        report = format_report(apk_path, hashes, zip_info, analysis)
        print(report)

        # Salvar relatório
        out_path = f"/tmp/{Path(apk_path).stem}_report.txt"
        Path(out_path).write_text(report, encoding="utf-8")
        print(f"\n[*] Relatório salvo em: {out_path}")


if __name__ == "__main__":
    main()
