import { useState, useEffect, useRef } from "react";
import { ShieldCheck } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

interface MFAProps {
  onComplete: () => void;
}

export default function MFA({ onComplete }: MFAProps) {
  const [qr, setQr] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<"enroll" | "verify" | null>(null);
  const called = useRef(false);

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    async function fetchSetup() {
      try {
        const res = await fetch("/api/mfa/setup", {
          method: "GET",
          credentials: "include",
        });

        if (res.ok) {
          setMode("enroll");
          const blob = await res.blob();
          setQr(URL.createObjectURL(blob));
        } else {
          setMode("verify");
        }
      } catch (err) {
        console.error(err);
        setMode("verify");
      } finally {
        setLoading(false);
      }
    }

    fetchSetup();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const res = await fetch("/api/mfa/validate", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });

      if (!res.ok) {
        setError(await res.text());
        return;
      }

      onComplete();
    } catch (err) {
      console.error(err);
      setError("MFA validation failed.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
        Loading…
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-900 rounded-xl p-8 shadow-2xl border border-slate-800">
          <div className="flex items-center gap-3 mb-6">
            <ShieldCheck className="w-6 h-6 text-teal-400" />
            <h2 className="text-xl font-semibold text-white">
              {mode === "enroll" ? "Set up Multi‑Factor Authentication" : "MFA Verification"}
            </h2>
          </div>

          {mode === "enroll" && qr && (
            <div className="flex flex-col items-center mb-6">
              <img
                src={qr}
                alt="MFA QR Code"
                className="mb-4 rounded-lg border border-slate-700"
              />
              <p className="text-slate-400 text-sm text-center max-w-sm">
                Scan this QR code with your authenticator app (Authy, Google Authenticator, etc.),
                then enter the 6‑digit code below.
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="code" className="text-white">Authentication Code</Label>
              <Input
                id="code"
                type="text"
                inputMode="numeric"
                placeholder="123456"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-teal-500 text-center tracking-widest"
                required
              />
            </div>

            <Button
              type="submit"
              className="w-full bg-teal-500 hover:bg-teal-600 text-white font-medium py-6 rounded-lg transition-colors"
            >
              {mode === "enroll" ? "Confirm & Enable MFA" : "Verify Code"}
            </Button>
          </form>

          {error && (
            <p className="mt-4 text-red-400 text-center text-sm">
              {error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
