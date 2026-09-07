import React, { useState, useEffect } from "react";
import { ChevronLeft, Save } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "./EditProfile.css";

const EditProfile = () => {
    const navigate = useNavigate();
    const [firstname, setFirstname] = useState("");
    const [lastname, setLastname] = useState("");
    const [email, setEmail] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        const fetchUserData = async () => {
            const userId = localStorage.getItem("user_id");
            if (userId) {
                try {
                    const res = await fetch(`/get_landlord_by_id/${userId}`);
                    if (res.ok) {
                        const data = await res.json();
                        const fullName = data.name || "";
                        const nameParts = fullName.split(" ");
                        setFirstname(nameParts[0] || "");
                        setLastname(nameParts.slice(1).join(" ") || "");
                        setEmail(data.email || "");
                    }
                } catch (error) {
                    console.error("Error fetching user data:", error);
                } finally {
                    setIsLoading(false);
                }
            }
        };
        fetchUserData();
    }, []);

    const handleUpdate = async (e) => {
        e.preventDefault();
        const userId = localStorage.getItem("user_id");
        if (!userId) return;

        setIsSaving(true);
        try {
            const res = await fetch(`/profile/${userId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: `${firstname} ${lastname}`,
                    email: email
                }),
            });

            if (res.ok) {
                alert("Profile updated successfully!");
                navigate("/account");
            } else {
                const err = await res.json();
                alert("Error: " + (err.error || "Failed to update profile"));
            }
        } catch (error) {
            console.error("Update error:", error);
            alert("Connection error");
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) return <div className="loading">Loading Profile...</div>;

    return (
        <motion.div
            className="edit-profile-container"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
        >
            <header className="edit-profile-header">
                <button className="back-btn" onClick={() => navigate("/account")}>
                    <ChevronLeft size={32} />
                </button>
                <h1>Edit Profile</h1>
            </header>

            <form className="edit-profile-form" onSubmit={handleUpdate}>
                <div className="input-group">
                    <label>First Name</label>
                    <input
                        type="text"
                        value={firstname}
                        onChange={(e) => setFirstname(e.target.value)}
                        placeholder="Enter your name"
                        required
                    />
                    <label>Last Name</label>
                    <input
                        type="text"
                        value={lastname}
                        onChange={(e) => setLastname(e.target.value)}
                        placeholder="Enter your Last name"
                        required
                    />
                </div>

                <div className="input-group">
                    <label>Email Address</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                        required
                    />
                </div>

                <motion.button
                    className="save-btn"
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={isSaving}
                >
                    <Save size={20} />
                    {isSaving ? "Saving Changes..." : "Update Profile"}
                </motion.button>
            </form>
        </motion.div>
    );
};

export default EditProfile;
