import {
  Alert,
  Box,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import type { ProcurementDetail } from "./api";
import { formatInr } from "./api";

function formatKg(value: string | number | null | undefined): string {
  const num = Number(value);
  if (!Number.isFinite(num) || num <= 0) return "—";
  return `${num.toLocaleString("en-IN", { maximumFractionDigits: 3 })} kg`;
}

function formatQuintals(kg: string | number): string {
  const num = Number(kg);
  if (!Number.isFinite(num) || num <= 0) return "—";
  return `${(num / 100).toLocaleString("en-IN", { maximumFractionDigits: 3 })} qtl`;
}

interface ProcurementWeightBreakdownProps {
  data: ProcurementDetail;
}

export function ProcurementWeightBreakdown({ data }: ProcurementWeightBreakdownProps) {
  const gross = Number(data.gross_weight_kg);
  const tare = Number(data.tare_weight_kg ?? 0);
  const kata = Number(data.bag_weight_deduction_kg);
  const net = Number(data.net_weight_kg);
  const weighed = gross > 0;
  const bagEntries = data.bag_entries ?? [];
  const bagSum = bagEntries.reduce((sum, row) => sum + Number(row.weight_kg), 0);

  const grossAmount = Number(data.gross_amount);
  const lineDeduction = Number(data.deduction_amount);
  const spotDeduction = Number(data.spot_deduction_amount);
  const netPayment = Number(data.net_amount);
  const priced = Number(data.rate_per_quintal) > 0 && grossAmount > 0;

  return (
    <Box>
      {!weighed && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Weights and payment amounts are not on the server yet. The manager must record weighment
          on the mobile app (or use the weighment action below). Until then, only bag count and
          planned rate from notes may appear.
        </Alert>
      )}

      <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
        Weight breakdown
      </Typography>
      <Table size="small" sx={{ mb: 2 }}>
        <TableBody>
          {bagEntries.length > 0 && (
            <TableRow>
              <TableCell>Sum of bag weights ({bagEntries.length} bags)</TableCell>
              <TableCell align="right">{formatKg(String(bagSum))}</TableCell>
            </TableRow>
          )}
          <TableRow>
            <TableCell>Gross weight (scale)</TableCell>
            <TableCell align="right">{formatKg(data.gross_weight_kg)}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Tare</TableCell>
            <TableCell align="right">{tare > 0 ? formatKg(data.tare_weight_kg) : "—"}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>
              Kata (per-bag deduction) — {data.per_bag_deduction_kg} kg × {data.bag_count} bags
            </TableCell>
            <TableCell align="right">{weighed ? formatKg(data.bag_weight_deduction_kg) : "—"}</TableCell>
          </TableRow>
          <TableRow sx={{ "& td": { fontWeight: 700 } }}>
            <TableCell>Net weight (payable)</TableCell>
            <TableCell align="right">{formatKg(data.net_weight_kg)}</TableCell>
          </TableRow>
          {weighed && (
            <TableRow>
              <TableCell>Net quintals</TableCell>
              <TableCell align="right">{formatQuintals(data.net_weight_kg)}</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {bagEntries.length > 0 && (
        <>
          <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
            Per-bag weighment (from mobile)
          </Typography>
          <Table size="small" sx={{ mb: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>Bag #</TableCell>
                <TableCell align="right">Weight (kg)</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {bagEntries.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.bag_number}</TableCell>
                  <TableCell align="right">{formatKg(row.weight_kg)}</TableCell>
                </TableRow>
              ))}
              <TableRow sx={{ "& td": { fontWeight: 600 } }}>
                <TableCell>Total</TableCell>
                <TableCell align="right">{formatKg(String(bagSum))}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </>
      )}

      <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
        Payment breakdown
      </Typography>
      <Table size="small">
        <TableBody>
          <TableRow>
            <TableCell>
              Gross amount
              {priced && ` (${formatQuintals(data.net_weight_kg)} × ${formatInr(data.rate_per_quintal)}/qtl)`}
            </TableCell>
            <TableCell align="right">{priced ? formatInr(data.gross_amount) : "—"}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Line deductions</TableCell>
            <TableCell align="right">
              {lineDeduction > 0 ? formatInr(data.deduction_amount) : "—"}
            </TableCell>
          </TableRow>
          {data.is_spot_payment && (
            <TableRow>
              <TableCell>
                Spot payment deduction (₹{data.spot_deduction_per_quintal}/qtl on net quintals)
              </TableCell>
              <TableCell align="right">
                {spotDeduction > 0 ? formatInr(data.spot_deduction_amount) : "—"}
              </TableCell>
            </TableRow>
          )}
          <TableRow sx={{ "& td": { fontWeight: 700 } }}>
            <TableCell>Net payment to farmer</TableCell>
            <TableCell align="right">{priced ? formatInr(data.net_amount) : "—"}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Box>
  );
}
