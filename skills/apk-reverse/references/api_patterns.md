# Suspicious Android API Patterns

## High-Risk APIs

### SMS Communication

```text
Landroid/telephony/SmsManager;->sendTextMessage
Landroid/telephony/SmsManager;->sendMultipartTextMessage
Landroid/content/ContentResolver;->query (with sms:// URI)
```

**Impact**: The app may send SMS messages without the user's knowledge (financial cost, data exfiltration)

---

### Access to Device Information

```text
Landroid/telephony/TelephonyManager;->getDeviceId      # IMEI
Landroid/telephony/TelephonyManager;->getSubscriberId  # IMSI
Landroid/telephony/TelephonyManager;->getLine1Number   # SIM phone number
Landroid/telephony/TelephonyManager;->getSimSerialNumber
```

**Impact**: Unique device/user fingerprinting

---

### Location

```text
Landroid/location/LocationManager;->getLastKnownLocation
Landroid/location/LocationManager;->requestLocationUpdates
Landroid/location/LocationManager;->addGpsStatusListener
```

**Impact**: Continuous location tracking

---

### Code Execution / Privilege Escalation

```text
Ljava/lang/Runtime;->exec            # executes shell commands
Ljava/lang/ProcessBuilder;->start   # same
Ljava/lang/reflect/Method;->invoke  # reflection (can hide behavior)
Ldalvik/system/DexClassLoader;->loadClass  # loads external code (dynamic loading)
Ldalvik/system/PathClassLoader;->loadClass
```

**Impact**: The app may download and execute malicious code at runtime

---

### Network

```text
Ljava/net/URL;->openConnection
Ljava/net/Socket;->connect
Lorg/apache/http/impl/client/DefaultHttpClient;->execute
Lokhttp3/OkHttpClient;->newCall
```

**Impact**: Communication with external servers (exfiltration, C2)

---

### Device Administration

```text
Landroid/app/admin/DevicePolicyManager;->lockNow        # locks the device
Landroid/app/admin/DevicePolicyManager;->wipeData       # wipes data (ransomware!)
Landroid/app/admin/DevicePolicyManager;->setPasswordQuality
Landroid/app/admin/DevicePolicyManager;->resetPassword
```

**Impact**: Full device control — typical of ransomware

---

### Camera and Microphone

```text
Landroid/hardware/Camera;->open
Landroid/hardware/camera2/CameraManager;->openCamera
Landroid/media/MediaRecorder;->setAudioSource
Landroid/media/AudioRecord;-><init>
```

**Impact**: Camera/microphone surveillance

---

### Cryptography (obfuscation/ransomware context)

```text
Ljavax/crypto/Cipher;->getInstance
Ljavax/crypto/Cipher;->doFinal
Ljava/security/KeyPairGenerator;->generateKeyPair
```

**Impact**: May be legitimate OR used for file encryption (ransomware)

---

## Anti-Analysis Techniques

### Emulator Detection

```python
# Strings to search for
"generic", "goldfish", "sdk", "emulator", "android sdk"
"Build.FINGERPRINT", "isEmulator"
```

### Root Detection

```python
# Strings to search for
"su", "/system/xbin/su", "/system/bin/su"
"Superuser.apk", "com.noshufou.android.su"
"RootBeer", "RootTools"
```

### Dynamic Loading (external code loading)

```text
DexClassLoader      # loads external DEX/JAR
PathClassLoader
InMemoryDexClassLoader  # loads DEX from memory (highly suspicious)
```

---

## Highly Suspicious Combinations

| Combination                                         | Indication                  |
| --------------------------------------------------- | --------------------------- |
| `RECEIVE_BOOT_COMPLETED` + `Service` + `SmsManager` | Persistent SMS trojan       |
| `DevicePolicyManager.wipeData` + `Cipher`           | Ransomware                  |
| `DexClassLoader` + external URL                     | Dropper (downloads malware) |
| `Runtime.exec` + `su` string                        | Root attempt                |
| `Camera` + `Socket`                                 | Camera spyware              |
| `TelephonyManager.getDeviceId` + HTTP request       | IMEI exfiltration           |
