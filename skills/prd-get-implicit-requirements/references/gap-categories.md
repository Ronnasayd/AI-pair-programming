# Gap Categories (Phase 2)

For each category ask: _does PRD define behavior for this scenario?_ Severity: **Critical** (blocks dev/distribution/legal risk) · **Important** (impacts architecture/core UX) · **Nice-to-have** (refinement).

## 2.1 Interface States

- Loading state? Empty state? Error state?
- Skeleton/spinner/placeholder defined?

## 2.2 Error Handling

- Behavior when each external integration fails?
- Auto-retry policy (backoff, limit)?
- Errors shown to user or silent?
- Fallback when service unavailable?

## 2.3 Navigation and Flow

- Back button behavior per screen?
- State preserved on navigate-away/return?
- Deep linking / direct URL access supported?
- Non-existent route handling?

## 2.4 Data and Persistence

- Cache TTL per data type?
- Schema migration on version upgrade?
- Max local storage size? Storage-full behavior?

## 2.5 Network and Connectivity

- Offline: block, degrade, or cache-serve?
- Timeouts by request type?
- HTTP vs HTTPS allowed where?
- Connection drop mid-critical-operation?

## 2.6 Security

- Sensitive data storage (where/how)?
- Session expiry behavior mid-use?
- Screenshot/clipboard/log capture rules?
- Input validation: client, server, both?

## 2.7 Performance

- List volume limit before pagination/virtualization?
- Heavy asset caching + max size?
- Progress feedback for long ops?
- Acceptable timeout per op before error?

## 2.8 Platform Behavior

- Required system permissions?
- Background/foreground transition behavior?
- Screen orientation locked or free?
- System notification interference handling?

## 2.9 Missing or Invalid Content

- Image/asset load failure fallback?
- Missing optional data: hide field or placeholder?
- Content expired/removed at source display?

## 2.10 Localization and Internationalization

- Date/time/currency/number: device locale or fixed?
- RTL language support (Arabic, Hebrew)?
- Pluralizable strings handled?
- User-generated content encoding?

## 2.11 Accessibility

- Screen reader support?
- Min touch target size?
- Min color contrast defined?
- Keyboard/remote nav required?

## 2.12 Legal and Compliance

- Consent required (GDPR, LGPD, CCPA)?
- Privacy policy accessible in-product?
- Terms shown before critical actions?
- Age classification required?

## 2.13 Deployment and Distribution

- Delivery format (bundle/package/container/binary)?
- Max artifact size?
- Code obfuscation/protection required?
- Update process: manual/auto/OTA?

## 2.14 Observability

- Which error events logged?
- PII in logs — handling?
- Crash reporting on by default?
- Performance metrics collected?
