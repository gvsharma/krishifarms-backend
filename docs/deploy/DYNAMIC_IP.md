# Dynamic EC2 IP — drop the Elastic IP

The shared dev EC2 (`gamya-couture-dev-api`, `i-0426cdc00ff15bfe9`) currently
keeps a static public IP (`13.232.200.243`). If that address is an **Elastic
IP**, AWS bills for it while the instance is stopped (~₹2000+/mo idle) — and
this project's EC2 is stopped ~13h/day by the cost scheduler.

This doc covers: releasing the EIP, running on the dynamic public IP, and
what must be updated on every IP change. **No repo change is needed per boot
— `deploy.yml` already resolves the live public IP** via `describe-instances`
at deploy time.

## Cost note

- Elastic IP attached to a **running** instance: free. Attached to a
  **stopped** instance (or unattached): billed per hour (~$0.005/h → ~$3.60/mo
  per address, plus AWS India taxes/fees on the invoice).
- A dynamic public IP (default on start, released on stop) costs nothing.
- If the bill shows a much larger EIP line item, check for **unattached**
  addresses or EIPs in other regions — releasing just this one may not be the
  whole story (see verification below).

## Recommended setup (dynamic IP, zero new cost)

1. Release the EIP (console/CLI steps below — user does this, not CI).
2. EC2 gets a fresh dynamic public IP on every start; nothing is paid idle.
3. Deploy, wake, health checks, and smoke tests resolve the live IP
   automatically (`deploy.yml` `ec2_target` step, `wake-ec2.yml`,
   `deploy/scripts/start-shared-ec2.sh`, `resolve-ec2-ip.sh`).
4. The **only** per-boot manual step: point Vercel at the new IP
   (dashboard env + redeploy), unless a stable DNS name is added (Option B).

## Option B (recommended if boots are frequent): stable DNS via Route 53

A hosted zone costs ~$0.50/mo + pennies per million queries — far below EIP
idle charges — and removes the Vercel update on every boot:

1. Create (or reuse) a Route 53 hosted zone for a domain you own
   (e.g. `api-dev.example.com` → A record, TTL 60–300s).
2. Point Vercel `API_PROXY_TARGET` at the DNS name **once**
   (`http://api-dev.example.com:8082`).
3. Update the A record on every boot — pick one:
   - `deploy.yml` step after `ec2_target` (Route 53 `change-resource-record-sets`
     from the resolved `ec2_host`; needs `route53:ChangeResourceRecordSets` on
     the deploy role), or
   - EC2 user-data / cron with an instance-profile role (needs
     `ec2:DescribeInstances` self + `route53:ChangeResourceRecordSets`), or
   - manually after `bash deploy/scripts/start-shared-ec2.sh --wait`.
4. Not implemented in this repo yet — file it as a follow-up if wakeups are
   more than ~weekly. The `patches/krishifarms-infra-deploy-iam-supabase.patch`
   already references Route 53 record management in `krishifarms-infra`, so the
   natural home for the zone/record is that repo.

## What NOT to change

| Concern | Status with dynamic IP |
|---------|------------------------|
| `deploy.yml` SSM deploy | Already dynamic — resolves `PublicIpAddress` live; `EC2_HOST` variable is now **optional** (kept only as a pinned override) |
| SSH / known_hosts | Nothing to update — GitHub runners never SSH; all EC2 access is via **SSM Session Manager**, which uses the instance ID, not the IP |
| `CORS_ORIGINS` | No change — it lists the Vercel site URL + localhost, never the EC2 IP |
| Security groups | No change — nginx `:8082` ingress rules are port-based, not source-IP based for the proxy path |
| Tailscale | Not in use in this project — do **not** introduce it for this; SSM already covers operator access and Vercel still needs a public endpoint |

## On every EC2 (re)start — update checklist

Run after `bash deploy/scripts/start-shared-ec2.sh --wait` (or the
**Wake shared EC2** workflow, which prints the live IP):

```bash
NEW_IP="$(bash deploy/scripts/resolve-ec2-ip.sh)"
echo "$NEW_IP"
curl -sf "http://${NEW_IP}:8082/api/v1/health"
```

| # | Setting | Where | Action |
|---|---------|-------|--------|
| 1 | `API_PROXY_TARGET` | Vercel dashboard → project → Settings → Environment Variables (Production) | Set to `http://${NEW_IP}:8082`, then **Redeploy** (env changes need a new deployment) |
| 2 | `EC2_HOST` | GitHub repo Variables (`gvsharma/krishifarms-backend`) | Optional — deploy auto-resolves; update or **delete** the variable so nothing references a stale IP |
| 3 | `E2E_API_PROXY_TARGET` | GitHub repo Variables (only if created) | Set to `http://${NEW_IP}:8082`, or leave unset (workflow defaults are overridden the same way) |
| 4 | Local testing | Your shell | `export API_HOST=http://${NEW_IP}:8082` for `scripts/smoke-test-api.sh` / `docs/DEMO_DATA.md` curl snippets |

`frontend/vercel.json` still carries the last-known IP as a fallback default —
dashboard env vars override it. After switching to Option B (DNS), replace the
`vercel.json` value with the DNS name once and stop touching it per boot.

## Releasing the Elastic IP (user action — AWS console or CLI)

> Do this **while the instance is running** (or accept a new dynamic IP on the
> next start). Releasing is irreversible — the address returns to the pool.

**First, confirm which address is the EIP:**

```bash
aws ec2 describe-addresses --region ap-south-1 \
  --query 'Addresses[].[PublicIp,InstanceId,AssociationId,AllocationId]' \
  --output table
aws ec2 describe-addresses --region ap-south-1 \
  --query 'Addresses[?AssociationId==`null`].[PublicIp,AllocationId]' \
  --output table   # unattached EIPs = pure idle billing; release first
```

Console path: **EC2 → Network & Security → Elastic IPs** (region `ap-south-1`)
→ select the address → **Actions → Release Elastic IP address**.

CLI path:

```bash
# If associated with the instance, disassociate first:
aws ec2 disassociate-address --region ap-south-1 --association-id eipassoc-XXXX
# Then release (frees the allocation; billing stops):
aws ec2 release-address --region ap-south-1 --allocation-id eipalloc-XXXX
```

**Verify billing stopped:**

```bash
aws ec2 describe-addresses --region ap-south-1 --output table  # should be empty
```

Then check **Billing → Bills → Elastic Compute Cloud** next invoice: the
`EIP idle surcharge` line should be gone. Repeat `describe-addresses` in every
region you use — EIPs in unused regions are a classic surprise charge.

## Trade-offs

| Approach | Cost | Vercel per boot | Downtime window |
|----------|------|-----------------|-----------------|
| Elastic IP (today) | ~₹2000+/mo idle on stopped instance | None | None (IP stable) |
| Dynamic IP + manual Vercel update (this doc) | **₹0** | Update env + redeploy (~2 min) | API unreachable via Vercel until updated; direct-IP clients also stale |
| Dynamic IP + Route 53 DNS (Option B) | ~₹45/mo zone | None (DNS TTL ~1–5 min propagation) | DNS TTL window only |

Stop/start itself always drops in-flight connections; that is unchanged by this
work — the cost scheduler already stops the host daily.
