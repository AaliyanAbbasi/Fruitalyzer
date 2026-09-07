import React, { useState, useRef } from "react";
import { ChevronLeft } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate, useLocation } from "react-router-dom";
import "./LiveDetection.css";

import liveFeedImg from "./assets/uploaded_media_1771677046028.jpg";
import { image, summary } from "framer-motion/client";
import { list } from "postcss";

const LiveDetection = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [result,setresult]=useState();

    const fileInputRef = useRef(null);
    const [imageSrc, setImageSrc] = useState(liveFeedImg);


    // Get selected farm data from navigation state
    const[date,setdate]=useState("");
    const farmId = location.state?.farmId;
    const farmName = location.state?.farmName || "Selected Farm";
    const [detectionResults, setDetectionResults] = useState(null);
    const [accumulatedResults, setAccumulatedResults] = useState({ classA: 0, classB: 0, classC: 0, totalWeight: 0, fruitName: "",image:"",confidence:0 });
    const [isProcessing, setIsProcessing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const sessionStartRef = useRef(null); // records when first image was uploaded this session

    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setErrorMsg("");
        setIsProcessing(true);
        // Record session start time on first upload of this session
        if (!sessionStartRef.current) {
            sessionStartRef.current = new Date().toISOString();
        }
        const imageUrl = URL.createObjectURL(file);
        setImageSrc(imageUrl);
    

        try {
            // 1. Predict the result by uploading the image
            const formData = new FormData();
            formData.append("image", file);

            const predictRes = await fetch("/predict", {
                method: "POST",
                body: formData,
            });
            const predictData = await predictRes.json();
            if(predictData.ok){
                setresult(predictData);
              
            }

            if (!predictRes.ok) {
                setErrorMsg(predictData.error || predictData.message || "Failed to predict image.");
                setIsProcessing(false);
                return;
            }
                // New response format: prediction fields are nested inside predictData.result
            const result = predictData.result || {};
            const isDetected = result.fruit && result.fruit !== "unknown" && result.grade;

            // Calculate classes based on prediction grade
            let classA = isDetected && result.grade === 'A' ? 1 : 0;
            let classB = isDetected && result.grade === 'B' ? 1 : 0;
            let classC = isDetected && result.grade === 'C' ? 1 : 0;

            // Add 1 unit weight if detected
            let weight = isDetected ? 1.0 : 0;
            let confidence = result.confidence || 0;

            // Accumulate results
            setAccumulatedResults(prev => ({
                classA: prev.classA + classA,
                classB: prev.classB + classB,
                classC: prev.classC + classC,
                totalWeight: prev.totalWeight + weight,
                fruitName: isDetected ? result.fruit : (prev.fruitName || "unknown"),
                confidence: confidence
            }));

            // Update UI with the latest prediction (including category)
            setDetectionResults({
                fruit: result.fruit || "unknown",
                grade: result.grade || "None",
                category: result.category || "",
                categoryConfidence: result.category_confidence || 0
            });

        } catch (error) {
            console.error("Error processing image:", error);
            setErrorMsg("An error occurred while connecting to the server.");
        } finally {
            setIsProcessing(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        }
        
    };

    const handleStopConveyor = async () => {
        if (!sessionStartRef.current) {
            setErrorMsg("No images scanned yet. Upload images first.");
            return;
        }

        setIsSaving(true);
        setErrorMsg("");

        try {
            const batchRes = await fetch("/save_temp_to_batch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    farm_id: farmId || 1
                })
            });

            const batchData = await batchRes.json();

            if (!batchRes.ok) {
                console.error("Failed to save batch", batchData);
                setErrorMsg(batchData.detail || batchData.error || batchData.message || "Failed to save batch.");
            } else {
                const finalBatchData = {
                    classA: accumulatedResults.classA,
                    classB: accumulatedResults.classB,
                    classC: accumulatedResults.classC,
                    batchId: batchData.batch_id,
                    farmId: farmId || 1
                };
                
                // Reset session so next scan starts fresh
                sessionStartRef.current = null;
                setAccumulatedResults({ classA: 0, classB: 0, classC: 0, totalWeight: 0, fruitName: "", image: "", confidence: 0 });
                setDetectionResults(null);

                navigate("/prediction-graph", { state: { batchData: finalBatchData } });
            }
        } catch (error) {
            console.error("Error saving batch:", error);
            setErrorMsg("An error occurred while saving the batch.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleResultChange = (e) => {
        const { name, value } = e.target;
        setDetectionResults(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handlesummary = async () => {
        // Pass the session start time so Summary only shows predictions from this session
        navigate("/summary", { state: { farmId, farmName, sessionStart: sessionStartRef.current } });
    };


    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: { type: "spring", stiffness: 100 }
        }
    };

    return (
        <motion.div
            className="live-detection-container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <div className="live-detection-card">
                <input type="date" name="setdate" id="1" />
                <header className="live-detection-header">
                    <button className="back-btn" onClick={() => navigate("/home")}>
                        <ChevronLeft size={32} />
                    </button>
                </header>

                <motion.h1 className="live-detection-title" variants={itemVariants}>
                    Live View
                </motion.h1>

                <motion.div className="feed-container" variants={itemVariants}>
                    <img src={imageSrc} alt="Live Conveyor Feed" className="live-feed-img" />
                    {isProcessing && (
                        <div className="processing-overlay" style={{
                            position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
                            display: "flex", justifyContent: "center", alignItems: "center",
                            backgroundColor: "rgba(0,0,0,0.5)", color: "white", fontSize: "1.2rem", borderRadius: "12px"
                        }}>
                            Processing Image...
                        </div>
                    )}
                </motion.div>

                {/* Results Display */}
                <motion.div className="results-container" variants={itemVariants} style={{
                    marginTop: "1rem", padding: "1rem", backgroundColor: "#f8fafc", borderRadius: "8px",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.1)", textAlign: "center"
                }}>
                    <h3 style={{ marginBottom: "0.8rem", color: "#334155" }}>Accumulated Batch Results</h3>
                    <div style={{ display: "flex", justifyContent: "space-around", flexWrap: "wrap", gap: "10px", color: "#475569" }}>
                        <div><strong>Class A:</strong> {accumulatedResults.classA}</div>
                        <div><strong>Class B:</strong> {accumulatedResults.classB}</div>
                        <div><strong>Class C:</strong> {accumulatedResults.classC}</div>
                        <div><strong>Total Count:</strong> {accumulatedResults.totalWeight.toFixed(0)}</div>
                        <div><strong>Confidence:</strong> {accumulatedResults.confidence ? `${(accumulatedResults.confidence * 100).toFixed(1)}%` : "—"}</div>
                    </div>
                    {detectionResults && (
                        <div style={{ marginTop: "10px", padding: "8px 12px", backgroundColor: "#e2e8f0", borderRadius: "6px", textAlign: "left", display: "flex", flexDirection: "column", gap: "4px" }}>
                            <div><strong>🍎 Fruit:</strong> {detectionResults.fruit}</div>
                            <div><strong>📊 Grade:</strong> {detectionResults.grade}</div>
                            {detectionResults.category && (
                                <div><strong>🏷️ Category:</strong> {detectionResults.category}
                                    {detectionResults.categoryConfidence > 0 && (
                                        <span style={{ color: "#64748b", fontSize: "12px", marginLeft: "6px" }}>
                                            ({(detectionResults.categoryConfidence * 100).toFixed(1)}% confidence)
                                        </span>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </motion.div>

                {errorMsg && <p className="error-message" style={{ color: "#ef4444", textAlign: "center", marginTop: "1rem" }}>{errorMsg}</p>}

                <motion.div className="controls-container" variants={itemVariants}>
                    <input
                        type="file"
                        accept="image/*"
                        ref={fileInputRef}
                        style={{ display: "none" }}
                        onChange={handleImageUpload}
                    />
                    <motion.button
                        className="control-btn start-btn"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => fileInputRef.current.click()}
                        disabled={isProcessing || isSaving}
                        style={{ opacity: (isProcessing || isSaving) ? 0.7 : 1, cursor: (isProcessing || isSaving) ? "not-allowed" : "pointer" }}
                    >
                        {isProcessing ? "Uploading..." : "Upload Image"}
                    </motion.button>
                    <motion.button
                        className="control-btn stop-btn"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleStopConveyor}
                        disabled={isProcessing || isSaving}
                        style={{ opacity: (isProcessing || isSaving) ? 0.7 : 1, cursor: (isProcessing || isSaving) ? "not-allowed" : "pointer", backgroundColor: "#dc2626" }}
                    >
                        {isSaving ? "Saving..." : "Summary"}
                    </motion.button>
                    <motion.button
                        className="control-btn stop-btn"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handlesummary}
                        
                        disabled={isProcessing || isSaving}
                        style={{ opacity: (isProcessing || isSaving) ? 0.7 : 1, cursor: (isProcessing || isSaving) ? "not-allowed" : "pointer", backgroundColor: "#dc2626" }}
                    >
                        {"Stop"}
                    </motion.button>

                

                </motion.div>
            </div>
        </motion.div>
    );
};

export default LiveDetection;


