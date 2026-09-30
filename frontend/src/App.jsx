import { useEffect, useState } from "react";
import { Routes, Route, Link, Navigate, useNavigate, useParams } from "react-router-dom";
import api, { clearToken, getToken, saveToken } from "./api";

function Home() {

  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">AI-ASSISTED DISPUTE RESOLUTION</p>
          <h1>FairResolve <span>AI</span></h1>
          <p className="lead">
            Explainable AI-assisted dispute resolution for faster, fairer and
            more transparent chargeback decisions.
          </p>
          
          <div className="actions">
            <Link className="button primary" to="/register">
              Create account
            </Link>

            <Link className="button secondary" to="/login">
              Login
            </Link>
          </div>
        </div>

        <div className="hero-card">
          <div className="status">● SYSTEM ONLINE</div>
          <h3>Dispute Resolution Pipeline</h3>
          <div className="pipeline">
            <span>Evidence</span><b>→</b><span>AI Analysis</span><b>→</b><span>Decision</span>
          </div>
        </div>
      </section>
    </main>
  );
}

function ProtectedRoute({ children }) {
  const token = getToken();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function Dashboard() {
  const [user, setUser] = useState(null);
  const [disputes, setDisputes] = useState([]);
  const [cards, setCards] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [newCard, setNewCard] = useState({
  card_number: "",
  card_type: "Visa",
  });
  const [cardLoading, setCardLoading] = useState(false);
  const [cardError, setCardError] = useState("");
  const [cardSuccess, setCardSuccess] = useState("");

  const [newTransaction, setNewTransaction] = useState({
    transaction_id: "",
    order_id: "",
    merchant_name: "",
    amount: "",
    currency: "INR",
    payment_method: "CREDIT_CARD",
    card_id: "",
  });
  const [transactionLoading, setTransactionLoading] = useState(false);
  const [transactionError, setTransactionError] = useState("");
  const [transactionSuccess, setTransactionSuccess] = useState("");
  const [showAddCard, setShowAddCard] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [disputeForm, setDisputeForm] = useState({
    reason: "PRODUCT_NOT_RECEIVED",
    description: "",
  });
  const [disputeLoading, setDisputeLoading] = useState(false);
  const [disputeError, setDisputeError] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

useEffect(() => {
  async function loadDashboard() {
    try {
      const [userResponse, disputesResponse] = await Promise.all([
        api.get("/api/auth/me"),
        api.get("/api/disputes"),
      ]);

      const currentUser = userResponse.data;

      setUser(currentUser);
      setDisputes(disputesResponse.data);

      if (currentUser.role?.toUpperCase() === "CUSTOMER") {
        const [cardsResponse, transactionsResponse] = await Promise.all([
          api.get("/api/cards"),
          api.get("/api/transactions"),
        ]);

        setCards(cardsResponse.data);
        setTransactions(transactionsResponse.data);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to load dashboard"
      );
    } finally {
      setLoading(false);
    }
  }

  loadDashboard();
}, []);

  function logout() {
    clearToken();
    window.location.href = "/";
  }

async function addCard() {
  setCardLoading(true);
  setCardError("");
  setCardSuccess("");

  try {
    const response = await api.post("/api/cards", newCard);

    setCards((prev) => [...prev, response.data]);

    setNewTransaction((prev) => ({
      ...prev,
      card_id: String(response.data.id),
    }));

    setNewCard({
      card_number: "",
      card_type: "Visa",
    });

    setShowAddCard(false);
    setCardSuccess("Card added and selected successfully.");
  } catch (err) {
    setCardError(
      err.response?.data?.detail || "Unable to add card"
    );
  } finally {
    setCardLoading(false);
  }
}

  async function addTransaction(e) {
    e.preventDefault();

    setTransactionLoading(true);
    setTransactionError("");
    setTransactionSuccess("");

    try {
      const response = await api.post("/api/transactions", {
        ...newTransaction,
        amount: Number(newTransaction.amount),
        card_id:
          newTransaction.payment_method === "UPI"
            ? null
            : Number(newTransaction.card_id),
      });

      setTransactions((prev) => [response.data, ...prev]);

      setNewTransaction({
        transaction_id: "",
        order_id: "",
        merchant_name: "",
        amount: "",
        currency: "INR",
        payment_method: "CREDIT_CARD",
        card_id: "",
      });

      setTransactionSuccess("Purchase added successfully.");
    } catch (err) {
      setTransactionError(
        err.response?.data?.detail || "Unable to add purchase"
      );
    } finally {
      setTransactionLoading(false);
    }
  }

  async function raiseDispute(e) {
  e.preventDefault();

  if (!selectedTransaction) {
    return;
  }

  setDisputeLoading(true);
  setDisputeError("");

  try {
    const response = await api.post("/api/disputes", {
      transaction_id: selectedTransaction.transaction_id,
      reason: disputeForm.reason,
      description: disputeForm.description,
    });

    setDisputes((prev) => [response.data, ...prev]);

    setSelectedTransaction(null);

    setDisputeForm({
      reason: "PRODUCT_NOT_RECEIVED",
      description: "",
    });
  } catch (err) {
    setDisputeError(
      err.response?.data?.detail || "Unable to raise dispute"
    );
  } finally {
    setDisputeLoading(false);
  }
}

  if (loading) {
    return (
      <main className="page">
        <div className="card">
          <h2>Loading disputes...</h2>
        </div>
      </main>
    );
  }

  return (
    <main className="page">
      <div className="dashboard-topbar">
        <div>
          <span className="dashboard-user">
            {user?.name}
          </span>
          <span className="dashboard-role">
            {user?.role}
          </span>
        </div>

      <button className="button secondary" onClick={logout}>
        Logout
      </button>
    </div>

      {user?.role?.toUpperCase() === "MERCHANT" ? (
        <>
          <p className="eyebrow">MERCHANT DASHBOARD</p>
          <h1 className="dashboard-title">
            Dispute <span>Cases</span>
          </h1>
          <p className="lead">
            Review customer disputes, submit supporting evidence and
            evaluate the evidence-based resolution.
          </p>
        </>
      ) : user?.role?.toUpperCase() === "INVESTIGATOR" ? (
        <>
          <p className="eyebrow">INVESTIGATOR DASHBOARD</p>
          <h1 className="dashboard-title">
            Dispute <span>Review</span>
          </h1>
          <p className="lead">
            Review disputes, evaluate submitted evidence and assess
            AI-assisted resolution recommendations.
          </p>
        </>
      ) : (
        <>
          <p className="eyebrow">CUSTOMER DASHBOARD</p>
          <h1 className="dashboard-title">
            Your <span>Disputes</span>
          </h1>
          <p className="lead">
            Track your disputes, review their status and view the
            evidence-based resolution.
          </p>
        </>
      )}

    {user?.role?.toUpperCase() === "CUSTOMER" && (
      <>
    <div className="card customer-purchase-card">
      <p className="eyebrow">NEW PURCHASE</p>
      <h2>Add Purchase</h2>
      <p className="muted">
        Record a purchase that can later be disputed.
      </p>

      <form onSubmit={addTransaction} className="customer-form">
        <label>
          Transaction ID
          <input
            required
            value={newTransaction.transaction_id}
            onChange={(e) =>
              setNewTransaction({
                ...newTransaction,
                transaction_id: e.target.value,
              })
            }
            placeholder="TXN1005"
          />
        </label>

        <label>
          Order ID
          <input
            required
            value={newTransaction.order_id}
            onChange={(e) =>
              setNewTransaction({
                ...newTransaction,
                order_id: e.target.value,
              })
            }
            placeholder="ORD5005"
          />
        </label>

        <label>
          Merchant Name
          <input
            required
            value={newTransaction.merchant_name}
            onChange={(e) =>
              setNewTransaction({
                ...newTransaction,
                merchant_name: e.target.value,
              })
            }
            placeholder="ABC Electronics"
          />
        </label>

        <label>
          Amount
          <input
            required
            type="number"
            min="0"
            step="0.01"
            value={newTransaction.amount}
            onChange={(e) =>
              setNewTransaction({
                ...newTransaction,
                amount: e.target.value,
              })
            }
            placeholder="4999"
          />
        </label>

        <label>
          Currency
          <select
            value={newTransaction.currency}
            onChange={(e) =>
              setNewTransaction({
                ...newTransaction,
                currency: e.target.value,
              })
            }
          >
            <option value="INR">INR</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
          </select>
        </label>

        <label>
          Payment Method
          <select
            value={newTransaction.payment_method}
            onChange={(e) =>
              setNewTransaction({
                ...newTransaction,
                payment_method: e.target.value,
                card_id:
                  e.target.value === "UPI"
                    ? ""
                    : newTransaction.card_id,
              })
            }
          >
            <option value="UPI">UPI</option>
            <option value="CREDIT_CARD">Credit Card</option>
            <option value="DEBIT_CARD">Debit Card</option>
          </select>
        </label>

        {newTransaction.payment_method !== "UPI" && (
          <>
            <label>
              Card
              <select
                required
                value={newTransaction.card_id}
                onChange={(e) =>
                  setNewTransaction({
                    ...newTransaction,
                    card_id: e.target.value,
                  })
                }
              >
                <option value="">Select card</option>

                {cards.map((card) => (
                  <option key={card.id} value={card.id}>
                    {card.card_type} •••• {card.card_number.slice(-4)}
                  </option>
                ))}
              </select>
            </label>

            <div className="inline-card-box">
              {!showAddCard ? (
                <button
                  type="button"
                  className="button secondary"
                  onClick={() => {
                    setShowAddCard(true);
                    setCardError("");
                    setCardSuccess("");
                  }}
                >
                  + Add New Card
                </button>
              ) : (
                <>
                  <h3>Add New Card</h3>

                  <label>
                    Card Number
                    <input
                      value={newCard.card_number}
                      onChange={(e) =>
                        setNewCard({
                          ...newCard,
                          card_number: e.target.value,
                        })
                      }
                      placeholder="4111111111111111"
                    />
                  </label>

                  <label>
                    Card Type
                    <select
                      value={newCard.card_type}
                      onChange={(e) =>
                        setNewCard({
                          ...newCard,
                          card_type: e.target.value,
                        })
                      }
                    >
                      <option value="Visa">Visa</option>
                      <option value="Mastercard">Mastercard</option>
                      <option value="Amex">Amex</option>
                    </select>
                  </label>

                  <div className="inline-card-actions">
                    <button
                      type="button"
                      className="button primary"
                      onClick={addCard}
                      disabled={cardLoading || !newCard.card_number}
                    >
                      {cardLoading ? "Saving..." : "Save Card"}
                    </button>

                    <button
                      type="button"
                      className="button secondary"
                      onClick={() => setShowAddCard(false)}
                    >
                      Cancel
                    </button>
                  </div>

                  {cardSuccess && (
                    <p className="upload-success">
                      {cardSuccess}
                    </p>
                  )}

                  {cardError && (
                    <p className="error">
                      {cardError}
                    </p>
                  )}
                </>
              )}
            </div>
          </>
        )}

        <button
          className="button primary"
          type="submit"
          disabled={
            transactionLoading ||
            (
              newTransaction.payment_method !== "UPI" &&
              cards.length === 0
            )
          }
        >
          {transactionLoading ? "Adding..." : "Add Purchase"}
        </button>

        {newTransaction.payment_method !== "UPI" &&
          cards.length === 0 && (
            <p className="muted">
              Add a card first to create a card-based purchase.
            </p>
          )}

        {transactionSuccess && (
          <p className="upload-success">
            {transactionSuccess}
          </p>
        )}

        {transactionError && (
          <p className="error">
            {transactionError}
          </p>
        )}
      </form>
    </div>

    <div className="card customer-transactions">
      <p className="eyebrow">PURCHASE HISTORY</p>
      <h2>Transactions / Purchases</h2>

      {transactions.length === 0 ? (
        <p className="muted">No transactions yet.</p>
      ) : (
        <div className="transaction-list">
          {transactions.map((transaction) => {
            const existingDispute = disputes.find(
              (dispute) =>
                String(dispute.transaction_id) === String(transaction.id)
            );

            const isSelected =
              selectedTransaction?.id === transaction.id;

            return (
              <div
                className="transaction-item"
                key={transaction.id}
              >
                <div>
                  <strong>{transaction.transaction_id}</strong>

                  <p>
                    {transaction.merchant_name} ·{" "}
                    {transaction.order_id || "No order ID"} ·{" "}
                    {transaction.payment_method.replaceAll("_", " ")}
                  </p>
                </div>

                <div className="transaction-meta">
                  <strong>
                    {transaction.currency} {transaction.amount}
                  </strong>

                  <span>
                    {transaction.transaction_date
                      ? new Date(
                          transaction.transaction_date
                        ).toLocaleDateString()
                      : "—"}
                  </span>

                  {existingDispute ? (
                    <span className="dispute-raised">
                      Dispute Already Raised
                    </span>
                  ) : (
                    <button
                      type="button"
                      className="button secondary"
                      onClick={() => {
                        setSelectedTransaction(transaction);
                        setDisputeError("");
                      }}
                    >
                      Raise Dispute
                    </button>
                  )}
                </div>

                {isSelected && (
                  <form
                    className="raise-dispute-form"
                    onSubmit={raiseDispute}
                  >
                    <h3>Raise Dispute</h3>
                    <p className="raise-dispute-transaction">
                      {selectedTransaction?.transaction_id} ·{" "}
                      {selectedTransaction?.merchant_name} ·{" "}
                      {selectedTransaction?.currency}{" "}
                      {selectedTransaction?.amount}
                    </p>


                    <label>
                      Reason
                      <select
                        value={disputeForm.reason}
                        onChange={(e) =>
                          setDisputeForm({
                            ...disputeForm,
                            reason: e.target.value,
                          })
                        }
                      >
                        <option value="PRODUCT_NOT_RECEIVED">
                          Product Not Received
                        </option>
                        <option value="WRONG_PRODUCT">
                          Wrong Product Received
                        </option>
                        <option value="DAMAGED_PRODUCT">
                          Product Damaged
                        </option>
                        <option value="DUPLICATE_CHARGE">
                          Duplicate Charge
                        </option>
                      </select>
                    </label>

                    <label>
                      Description
                      <textarea
                        required
                        rows="4"
                        value={disputeForm.description}
                        onChange={(e) =>
                          setDisputeForm({
                            ...disputeForm,
                            description: e.target.value,
                          })
                        }
                        placeholder="Explain what happened with this purchase..."
                      />
                    </label>

                    <div className="raise-dispute-actions">
                      <button
                        type="submit"
                        className="button primary"
                        disabled={disputeLoading}
                      >
                        {disputeLoading
                          ? "Submitting..."
                          : "Submit Dispute"}
                      </button>

                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => {
                          setSelectedTransaction(null);
                          setDisputeError("");
                        }}
                      >
                        Cancel
                      </button>
                    </div>

                    {disputeError && (
                      <p className="error">{disputeError}</p>
                    )}
                  </form>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
      </>
    )}

      {error && <p className="error">{error}</p>}

      {!error && disputes.length === 0 && (
        <div className="card">
          <h2>
            {user?.role?.toUpperCase() === "CUSTOMER"
              ? "No disputes yet"
              : "No dispute cases found"}
          </h2>

          <p>
            {user?.role?.toUpperCase() === "CUSTOMER"
              ? "You haven't created any disputes yet."
              : "There are no dispute cases available at the moment."}
          </p>
        </div>
      )}

      <div className="dispute-grid">
        {disputes.map((dispute) => (
          <Link
            to={`/dashboard/dispute/${dispute.dispute_id}`}
            className="card dispute-card dispute-link"
            key={dispute.id}
          >
            <div className="dispute-header">
              <div>
                <p className="dispute-id">{dispute.dispute_id}</p>
                <h2>{dispute.reason.replaceAll("_", " ")}</h2>
              </div>

              <span
                className={`status-badge ${dispute.status.toLowerCase()}`}
              >
                {dispute.status.replaceAll("_", " ")}
              </span>
            </div>

            <p className="dispute-description">
              {dispute.description}
            </p>

            <p className="dispute-date">
              Created:{" "}
              {dispute.created_at
                ? new Date(dispute.created_at).toLocaleDateString()
                : "—"}
            </p>
          </Link>
        ))}
      </div>
    </main>
  );
}

function DisputeDetails() {
  const { disputeId } = useParams();

  const [dispute, setDispute] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [user, setUser] = useState(null);
  const [resolving, setResolving] = useState(false);
  const [resolveError, setResolveError] = useState("");

  useEffect(() => {
    async function loadDispute() {
      try {
        const [disputeResponse, evidenceResponse, auditResponse] = await Promise.all([
          api.get(`/api/disputes/${disputeId}`),
          api.get(`/api/disputes/${disputeId}/evidence`),
          api.get(`/api/disputes/${disputeId}/audit-logs`),
        ]);

        setDispute(disputeResponse.data);
        setEvidence(evidenceResponse.data);
        setAuditLogs(auditResponse.data);
      } catch (err) {
        setError(
          err.response?.data?.detail || "Unable to load dispute"
        );
      } finally {
        setLoading(false);
      }
    }

    api.get("/api/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => {});

    loadDispute();
  }, [disputeId]);

  async function runAnalysis() {
    setAnalysisLoading(true);
    setAnalysisError("");

  try {
    const response = await api.get(
      `/api/disputes/${disputeId}/analyze`
    );

    setAnalysis(response.data);

    const disputeResponse = await api.get(
      `/api/disputes/${disputeId}`
    );

    setDispute(disputeResponse.data);

  } catch (err) {
    setAnalysisError(
      err.response?.data?.detail || "Unable to analyze dispute"
    );
  } finally {
    setAnalysisLoading(false);
  }
}

  async function uploadEvidence() {
  if (!selectedFile) {
    setUploadError("Please select a file first.");
    return;
  }

  setUploading(true);
  setUploadError("");

  try {
    const formData = new FormData();
    formData.append("file", selectedFile);

    await api.post(
      `/api/disputes/${disputeId}/upload-evidence`,
      formData
    );

    // Refresh evidence list
    const response = await api.get(
      `/api/disputes/${disputeId}/evidence`
    );

    setEvidence(response.data);
    setSelectedFile(null);
    setUploadSuccess("Evidence uploaded successfully.");

  } catch (err) {
    setUploadError(
      err.response?.data?.detail || "Evidence upload failed"
    );
  } finally {
    setUploading(false);
  }
}

  async function resolveDispute() {
    setResolving(true);
    setResolveError("");

    try {
      const response = await api.patch(
        `/api/disputes/${disputeId}/resolve`
      );

      setDispute(response.data);

      const auditResponse = await api.get(
        `/api/disputes/${disputeId}/audit-logs`
      );

      setAuditLogs(auditResponse.data);

    } catch (err) {
      setResolveError(
        err.response?.data?.detail || "Unable to resolve dispute"
      );
    } finally {
      setResolving(false);
    }
  }

  if (loading) {
    return (
      <main className="page">
        <div className="card">
          <h2>Loading dispute details...</h2>
          <p className="muted">
            Please wait while we retrieve the case information.
          </p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page">
        <p className="error">{error}</p>
      </main>
    );
  }

  return (
    <main className="page">
      <Link to="/dashboard" className="back-link">
        ← Back to Disputes
      </Link>

      {user?.role?.toUpperCase() === "MERCHANT" ? (
        <p className="eyebrow">MERCHANT CASE REVIEW</p>
      ) : user?.role?.toUpperCase() === "INVESTIGATOR" ? (
        <p className="eyebrow">INVESTIGATOR CASE REVIEW</p>
      ) : (
        <p className="eyebrow">DISPUTE DETAILS</p>
      )}

      <div className="dispute-detail-header">
        <div>
          <p className="dispute-id">{dispute.dispute_id}</p>

          <h1 className="dashboard-title">
            {dispute.reason.replaceAll("_", " ")}
          </h1>
        </div>

        <span
          className={`status-badge ${dispute.status.toLowerCase()}`}
        >
          {dispute.status}
        </span>
      </div>

      {dispute.status === "RESOLVED" && (
        <div className="resolved-message">
          <strong>✓ Case Resolved</strong>
          <p>
            This dispute has been resolved and is now closed for further action.
          </p>
        </div>
      )}

      {user?.role?.toUpperCase() === "INVESTIGATOR" &&
        dispute.status !== "RESOLVED" && (
          <div className="investigator-action">
            <button
              className="button primary"
              onClick={resolveDispute}
              disabled={resolving}
            >
              {resolving ? "Resolving..." : "Resolve Case"}
            </button>

            {resolveError && (
              <p className="error">{resolveError}</p>
            )}
          </div>
        )}

      <div className="card">
        <h2>Description</h2>
        <p className="dispute-description">
          {dispute.description || "No description provided."}
        </p>

        <p className="dispute-date">
          Created:{" "}
          {dispute.created_at
            ? new Date(dispute.created_at).toLocaleDateString()
            : "—"}
        </p>
      </div>

      <div className="card">
        <h2>{user?.role?.toUpperCase() === "MERCHANT"
              ? "Supporting Evidence"
              : "Evidence"}</h2>

        {evidence.length === 0 ? (
          <p>No evidence submitted.</p>
        ) : (
          <div className="evidence-list">
            {evidence.map((item) => (
              <div className="evidence-item" key={item.id}>
                <div>
                  <strong>{item.file_name}</strong>

                  <p>
                    Type: {item.evidence_type}
                  </p>

                  <p>
                    Submitted by: {item.submitted_by}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

         {user?.role?.toUpperCase() !== "INVESTIGATOR" && 
          dispute.status !== "RESOLVED" && (
          <div className="upload-section">
            <h3>
              {user?.role?.toUpperCase() === "MERCHANT"
              ? "Submit Supporting Evidence"
              : "Add Evidence"}
            </h3>

            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(e) => {
                setSelectedFile(e.target.files[0] || null);
                setUploadError("");
                setUploadSuccess("");
              }}
            />

            <button
              className="button primary"
              onClick={uploadEvidence}
              disabled={uploading}
            >
              {uploading ? "Uploading..." : "Upload Evidence"}
            </button>

            {uploadSuccess && (
              <p className="upload-success">{uploadSuccess}</p>
            )}

            {uploadError && (
              <p className="error">{uploadError}</p>
            )}
          </div>
        )}

      </div>

      <div className="section-card audit-section">
        <div className="section-header">
          <div>
            <p className="eyebrow">AUDIT TRAIL</p>
            <h2 className="section-title">Audit History</h2>
          </div>
        </div>

        {auditLogs.length === 0 ? (
          <p className="muted">No audit activity recorded yet.</p>
        ) : (
          <div className="audit-list">
            {auditLogs.map((log) => (
              <div className="audit-item" key={log.id}>
                <div className="audit-item-header">
                  <strong>{log.action}</strong>
                  <span>
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                </div>

                <p>{log.details}</p>

                <small>Actor: {log.actor}</small>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card analysis-card">
        <div className="analysis-header">
          <div>
            {user?.role?.toUpperCase() === "MERCHANT" ? (
              <>
                <p className="eyebrow">FAIRRESOLVE AI</p>
                <h2>Case Evidence Analysis</h2>
              </>
            ) : (
              <>
                <p className="eyebrow">FAIRRESOLVE AI</p>
                <h2>AI Dispute Analysis</h2>
              </>
            )}
          </div>

          <button
            className="button primary"
            onClick={runAnalysis}
            disabled={analysisLoading}
          >
            {analysisLoading
              ? "Analyzing..."
              : user?.role?.toUpperCase() === "MERCHANT"
                ? "Analyze Case"
                : "Analyze Dispute"}
          </button>
        </div>

        {analysisError && (
          <p className="error">{analysisError}</p>
        )}

        {analysis && (
          <>
            <div className="score-grid">
              <div className="score-box">
                <span>Customer Score</span>
                <strong>{analysis.result.customer_score}</strong>
              </div>

              <div className="score-box">
                <span>Merchant Score</span>
                <strong>{analysis.result.merchant_score}</strong>
              </div>

              <div className="score-box">
                <span>    
                  {user?.role?.toUpperCase() === "MERCHANT"
                  ? "Resolution Confidence"
                  : "Confidence"}
                </span>
                <strong>{analysis.result.confidence}%</strong>
              </div>
            </div>

            <div className="decision-box">
              <p className="eyebrow">DECISION</p>
              <h2>
                {analysis.result.decision.replaceAll("_", " ")}
              </h2>
            </div>

            <div className="evidence-strength">
              <h3>Evidence Strength</h3>

              <div className="strength-row">
                <span>Customer Direct Evidence</span>
                <strong>
                  {analysis.result.customer_direct_evidence}
                </strong>
              </div>

              <div className="strength-row">
                <span>Merchant Direct Evidence</span>
                <strong>
                  {analysis.result.merchant_direct_evidence}
                </strong>
              </div>
            </div>

            <div className="analysis-columns">
              <div>
                <h3>Customer Evidence</h3>

                {analysis.result.customer_reasons.map(
                  (reason, index) => (
                    <p key={index} className="reason">
                      ✓ {reason}
                    </p>
                  )
                )}
              </div>

              <div>
                <h3>Merchant Evidence</h3>

                {analysis.result.merchant_reasons.map(
                  (reason, index) => (
                    <p key={index} className="reason">
                      ✓ {reason}
                    </p>
                  )
                )}
              </div>
            </div>
            
            {analysis.relevant_evidence?.length > 0 && (
              <div className="evidence-review-box">
                <h3>Relevant Evidence</h3>

                {analysis.relevant_evidence.map((evidence) => (
                  <div
                    className="evidence-review-item"
                    key={evidence.id}
                  >
                    <strong>{evidence.file_name}</strong>

                    <span>
                      {evidence.submitted_by} · {evidence.evidence_type}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {analysis.excluded_evidence?.length > 0 && (
              <div className="evidence-review-box">
                <h3>Excluded Evidence</h3>

                {analysis.excluded_evidence.map((evidence) => (
                  <div
                    className="evidence-review-item excluded"
                    key={evidence.evidence_id}
                  >
                    <strong>{evidence.file_name}</strong>

                    <span>{evidence.reason}</span>
                  </div>
                ))}
              </div>
            )}

            <div className="fact-comparison">
              <h3>Evidence Fact Comparison</h3>

              {Object.entries(analysis.result.fact_comparison || {}).map(
                ([fact, values]) => (
                  <div className="fact-row" key={fact}>
                    <div className="fact-name">
                      {fact.replaceAll("_", " ")}
                    </div>

                  <div className="fact-customer">
                    <span>Customer</span>
                    <strong>
                      {values.customer ?? "—"}
                    </strong>
                  </div>

                  <div className="fact-merchant">
                    <span>Merchant</span>
                    <strong>
                      {values.merchant ?? "—"}
                    </strong>
                  </div>

                  {values.match !== undefined ? (
                    <div
                      className={
                        values.match
                          ? "fact-match"
                          : "fact-mismatch"
                      }
                    >
                      {values.match ? "✓ Match" : "✕ Mismatch"}
                    </div>
                  ) : (
                    <div className="fact-no-match">
                      —
                    </div>
                  )}
                </div>
              )
            )}
          </div>

            {analysis.result.contradictions?.length > 0 && (
              <div className="contradiction-box">
                <h3>⚠ Contradiction Detected</h3>

                  {analysis.result.contradictions.map(
                    (contradiction, index) => (
                      <div key={index}>
                        <strong>
                          {contradiction.severity}
                        </strong>

                        <p>{contradiction.message}</p>
                      </div>
                    )
                  )}
                </div>
              )}

              {analysis.explanation && (
                <div className="explanation-box">
                  <h3>
                    {user?.role?.toUpperCase() === "MERCHANT"
                    ? "Case Resolution Explanation"
                    : "Decision Explanation"}
                  </h3>

                  <p>
                    <strong>Summary:</strong>{" "}
                    {analysis.explanation.summary}
                  </p>

                  <p>
                    <strong>Recommendation:</strong>{" "}
                    {analysis.explanation.recommendation}
                  </p>

                  <p>
                    <strong>Key Finding:</strong>{" "}
                    {analysis.explanation.key_finding}
                  </p>
                </div>
              )}
            </>
          )}
        </div>

    </main>
  );
}

function AuthForm({ mode }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "customer" });
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");

    try {
      if (mode === "register") {
        await api.post("/api/auth/register", form);
      }
      const login = await api.post("/api/auth/login", {
        email: form.email,
        password: form.password,
      });
      saveToken(login.data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={submit}>
          <Link to="/" className="auth-back-link">
            ← Back to Home
          </Link>
        <p className="eyebrow">FAIRRESOLVE AI</p>
        <h1>{mode === "register" ? "Create Account" : "Welcome Back"}</h1>

        {mode === "register" && (
          <>
            <label>Name<input required value={form.name} onChange={e => setForm({...form, name: e.target.value})} /></label>
            <label>Role
              <select value={form.role} onChange={e => setForm({...form, role: e.target.value})}>
                <option value="customer">Customer</option>
                <option value="merchant">Merchant</option>
                <option value="investigator">Investigator</option>
              </select>
            </label>
          </>
        )}

        <label>Email<input type="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})} /></label>
        <label>Password<input type="password" required minLength="6" value={form.password} onChange={e => setForm({...form, password: e.target.value})} /></label>

        {error && <p className="error">{error}</p>}

        <button className="button primary" type="submit">
          {mode === "register" ? "Create account" : "Login"}
        </button>

        <Link to={mode === "register" ? "/login" : "/register"}>
          {mode === "register" ? "Already have an account? Login" : "Need an account? Register"}
        </Link>
      </form>
    </main>
  );
}

function App() {
  return (
    <>
      <nav className="nav">
        <Link to="/" className="brand">FairResolve <span>AI</span></Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<AuthForm mode="register" />} />
        <Route path="/login" element={<AuthForm mode="login" />} />
        <Route path="/dashboard" element={<ProtectedRoute> <Dashboard /> </ProtectedRoute>} />
        <Route
          path="/dashboard/dispute/:disputeId"
          element={<ProtectedRoute> <DisputeDetails /> </ProtectedRoute>}
        />
      </Routes>
    </>
  );
}

export default App;
