import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Alert, AlertDescription } from "./ui/alert";
import { Badge } from "./ui/badge";

interface BankAccount {
  id: number;
  bankName: string;
  accountType: string;
  lastFour: string;
  isPrimary: boolean;
  createdAt: string;
}

interface BankAccountsProps {
  onClose?: () => void;
}

const COMMON_BANKS = [
  "Chase",
  "Bank of America",
  "Wells Fargo",
  "Citibank",
  "US Bank",
  "PNC Bank",
  "Capital One",
  "TD Bank",
  "Truist",
  "Other"
];

export default function BankAccounts({ onClose }: BankAccountsProps) {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Form state
  const [bankName, setBankName] = useState("");
  const [customBankName, setCustomBankName] = useState("");
  const [routingNumber, setRoutingNumber] = useState("");
  const [accountNumber, setAccountNumber] = useState("");
  const [confirmAccountNumber, setConfirmAccountNumber] = useState("");
  const [accountType, setAccountType] = useState<string>("checking");
  const [isPrimary, setIsPrimary] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/bank-accounts", {
        credentials: "include"
      });
      
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts || []);
      } else if (response.status === 401) {
        setError("Please log in to view bank accounts");
      } else {
        const data = await response.json();
        setError(data.error || "Failed to load bank accounts");
      }
    } catch (err) {
      setError("Failed to connect to server");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setBankName("");
    setCustomBankName("");
    setRoutingNumber("");
    setAccountNumber("");
    setConfirmAccountNumber("");
    setAccountType("checking");
    setIsPrimary(false);
    setShowAddForm(false);
  };

  const handleAddAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validation
    const finalBankName = bankName === "Other" ? customBankName : bankName;
    
    if (!finalBankName) {
      setError("Please select or enter a bank name");
      return;
    }

    if (routingNumber.length !== 9) {
      setError("Routing number must be exactly 9 digits");
      return;
    }

    if (accountNumber.length < 4 || accountNumber.length > 17) {
      setError("Account number must be 4-17 digits");
      return;
    }

    if (accountNumber !== confirmAccountNumber) {
      setError("Account numbers do not match");
      return;
    }

    try {
      setSubmitting(true);
      const response = await fetch("/api/bank-accounts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          bankName: finalBankName,
          routingNumber,
          accountNumber,
          accountType,
          isPrimary: accounts.length === 0 ? true : isPrimary
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess("Bank account added successfully!");
        resetForm();
        fetchAccounts();
      } else {
        setError(data.error || "Failed to add bank account");
      }
    } catch (err) {
      setError("Failed to connect to server");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteAccount = async (accountId: number) => {
    if (!confirm("Are you sure you want to remove this bank account?")) {
      return;
    }

    try {
      const response = await fetch(`/api/bank-accounts/${accountId}`, {
        method: "DELETE",
        credentials: "include"
      });

      if (response.ok) {
        setSuccess("Bank account removed successfully");
        fetchAccounts();
      } else {
        const data = await response.json();
        setError(data.error || "Failed to remove account");
      }
    } catch (err) {
      setError("Failed to connect to server");
    }
  };

  const handleSetPrimary = async (accountId: number) => {
    try {
      const response = await fetch(`/api/bank-accounts/${accountId}/primary`, {
        method: "PUT",
        credentials: "include"
      });

      if (response.ok) {
        setSuccess("Primary account updated");
        fetchAccounts();
      } else {
        const data = await response.json();
        setError(data.error || "Failed to update primary account");
      }
    } catch (err) {
      setError("Failed to connect to server");
    }
  };

  const formatRoutingNumber = (value: string) => {
    return value.replace(/\D/g, "").slice(0, 9);
  };

  const formatAccountNumber = (value: string) => {
    return value.replace(/\D/g, "").slice(0, 17);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                🏦 Bank Accounts
              </CardTitle>
              <CardDescription>
                Manage your linked bank accounts for deposits and withdrawals
              </CardDescription>
            </div>
            {onClose && (
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {success && (
            <Alert className="mb-4 bg-green-50 border-green-200">
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {/* Existing Accounts */}
              {accounts.length > 0 && (
                <div className="space-y-3 mb-6">
                  {accounts.map((account) => (
                    <div
                      key={account.id}
                      className="flex items-center justify-between p-4 border rounded-lg bg-gray-50"
                    >
                      <div className="flex items-center gap-4">
                        <div className="text-2xl">🏦</div>
                        <div>
                          <div className="font-medium flex items-center gap-2">
                            {account.bankName}
                            {account.isPrimary && (
                              <Badge variant="secondary" className="text-xs">
                                Primary
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-gray-600">
                            {account.accountType.charAt(0).toUpperCase() + account.accountType.slice(1)} •••• {account.lastFour}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {!account.isPrimary && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSetPrimary(account.id)}
                          >
                            Set Primary
                          </Button>
                        )}
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteAccount(account.id)}
                        >
                          Remove
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {accounts.length === 0 && !showAddForm && (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">🏦</div>
                  <p>No bank accounts linked yet</p>
                  <p className="text-sm">Add a bank account to enable deposits and withdrawals</p>
                </div>
              )}

              {/* Add Account Button */}
              {!showAddForm && accounts.length < 5 && (
                <Button
                  onClick={() => setShowAddForm(true)}
                  className="w-full"
                >
                  + Add Bank Account
                </Button>
              )}

              {accounts.length >= 5 && (
                <p className="text-center text-sm text-gray-500">
                  Maximum of 5 bank accounts reached
                </p>
              )}

              {/* Add Account Form */}
              {showAddForm && (
                <form onSubmit={handleAddAccount} className="space-y-4 border-t pt-6 mt-4">
                  <h3 className="font-semibold text-lg">Add New Bank Account</h3>
                  
                  <div className="space-y-2">
                    <Label htmlFor="bankName">Bank Name</Label>
                    <Select value={bankName} onValueChange={setBankName}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select your bank" />
                      </SelectTrigger>
                      <SelectContent>
                        {COMMON_BANKS.map((bank) => (
                          <SelectItem key={bank} value={bank}>
                            {bank}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {bankName === "Other" && (
                    <div className="space-y-2">
                      <Label htmlFor="customBankName">Enter Bank Name</Label>
                      <Input
                        id="customBankName"
                        value={customBankName}
                        onChange={(e) => setCustomBankName(e.target.value)}
                        placeholder="Enter your bank name"
                      />
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="accountType">Account Type</Label>
                    <Select value={accountType} onValueChange={setAccountType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="checking">Checking</SelectItem>
                        <SelectItem value="savings">Savings</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="routingNumber">Routing Number</Label>
                    <Input
                      id="routingNumber"
                      value={routingNumber}
                      onChange={(e) => setRoutingNumber(formatRoutingNumber(e.target.value))}
                      placeholder="9 digits"
                      maxLength={9}
                    />
                    <p className="text-xs text-gray-500">
                      The 9-digit number on the bottom left of your check
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="accountNumber">Account Number</Label>
                    <Input
                      id="accountNumber"
                      type="password"
                      value={accountNumber}
                      onChange={(e) => setAccountNumber(formatAccountNumber(e.target.value))}
                      placeholder="4-17 digits"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmAccountNumber">Confirm Account Number</Label>
                    <Input
                      id="confirmAccountNumber"
                      type="password"
                      value={confirmAccountNumber}
                      onChange={(e) => setConfirmAccountNumber(formatAccountNumber(e.target.value))}
                      placeholder="Re-enter account number"
                    />
                  </div>

                  {accounts.length > 0 && (
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="isPrimary"
                        checked={isPrimary}
                        onChange={(e) => setIsPrimary(e.target.checked)}
                        className="rounded"
                      />
                      <Label htmlFor="isPrimary" className="text-sm font-normal">
                        Set as primary account
                      </Label>
                    </div>
                  )}

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
                    <p className="font-medium mb-1">🔒 Your data is encrypted</p>
                    <p>
                      Bank account information is encrypted using industry-standard 
                      AES-256 encryption before being stored.
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={resetForm}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={submitting}
                      className="flex-1"
                    >
                      {submitting ? "Adding..." : "Add Bank Account"}
                    </Button>
                  </div>
                </form>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
