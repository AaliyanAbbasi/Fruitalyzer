import React, { useState, useEffect } from "react";
import { ChevronLeft, User, Lock, Trash2, Bell, ChevronRight, Camera, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "./Account.css";

const Account = () => {
    const navigate = useNavigate();
    const [userData, setUserData] = useState({
        name: "",
        email: "",
        profileImg: null
    });
    const [notifications, setNotifications] = useState(true);
    const [isPreviewOpen, setIsPreviewOpen] = useState(false);
    const fileInputRef = React.useRef(null);

    useEffect(() => {
        const fetchUserData = async () => {
            const userId = localStorage.getItem("user_id");
            if (userId) {
                try {
                    const res = await fetch(`/get_landlord_by_id/${userId}`);
                    if (res.ok) {
                        const data = await res.json();
                        setUserData ({
                            name: data.name,
                            email: data.email
                        });
                    }
                } catch (error) {
                    console.error("Error fetching user data:", error);
                }
            }
        };
        fetchUserData();
    }, []);

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setUserData(prev => ({
                    ...prev,
                    profileImg: event.target.result
                }));
            };
            reader.readAsDataURL(file);
        }
    };

    const triggerFileInput = () => {
        fileInputRef.current.click();
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const itemVariants = {
        hidden: { x: -20, opacity: 0 },
        visible: {
            x: 0,
            opacity: 1,
            transition: { type: "spring", stiffness: 100 }
        }
    };

    return (
        <motion.div
            className="account-container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <header className="account-header">
                <button className="back-btn" onClick={() => navigate("/home")}>
                    <ChevronLeft size={32} />
                </button>
                <h1>My Account</h1>
            </header>

            <motion.div className="profile-section" variants={itemVariants}>
                <div className="avatar-wrapper">
                    <div
                        className="avatar-main"
                        onClick={() => userData.profileImg && setIsPreviewOpen(true)}
                    >
                        {userData.profileImg ? (
                            <img src={userData.profileImg} alt="Profile" className="avatar-img" />
                        ) : (
                            <div className="avatar-placeholder">
                                <User size={40} />
                            </div>
                        )}
                    </div>
                    <button
                        className="camera-overlay"
                        onClick={(e) => {
                            e.stopPropagation();
                            triggerFileInput();
                        }}
                    >
                        <Camera size={20} />
                    </button>
                </div>
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleImageChange}
                    accept="image/*"
                    style={{ display: "none" }}
                />
                <div className="profile-info">
                    <h2>{userData.name}</h2>
                    <p>{userData.email}</p>
                </div>
            </motion.div>

            <motion.div className="manage-title" variants={itemVariants}>
                <span>Manage </span>
                <span>Your Account</span>
            </motion.div>

            <div className="settings-list">
                <motion.div
                    className="settings-item"
                    variants={itemVariants}
                    onClick={() => navigate("/edit-profile")}
                >
                    <div className="settings-icon"><User size={22} /></div>
                    <span className="settings-label">Edit Profile</span>
                    <div className="settings-action"><ChevronRight size={20} /></div>
                </motion.div>

                <motion.div className="settings-item" variants={itemVariants}>
                    <div className="settings-icon"><Lock size={22} /></div>
                    <span className="settings-label">Change Your Password</span>
                    <div className="settings-action"><ChevronRight size={20} /></div>
                </motion.div>

                <motion.div className="settings-item" variants={itemVariants}>
                    <div className="settings-icon"><Trash2 size={22} /></div>
                    <span className="settings-label">Delete Account</span>
                    <div className="settings-action"><ChevronRight size={20} /></div>
                </motion.div>

                <motion.div className="settings-item" variants={itemVariants}>
                    <div className="settings-icon"><Bell size={22} /></div>
                    <span className="settings-label">Notification</span>
                    <div className="settings-action">
                        <div
                            className={`toggle-switch ${notifications ? 'on' : ''}`}
                            onClick={() => setNotifications(!notifications)}
                        >
                            <div className="toggle-handle"></div>
                        </div>
                    </div>
                </motion.div>
            </div>

            <motion.div className="logout-container" variants={itemVariants}>
                <button className="logout-btn" onClick={() => { localStorage.removeItem('user_id'); navigate("/") }}>
                    LOG OUT
                </button>
            </motion.div>

            <AnimatePresence>
                {isPreviewOpen && (
                    <motion.div
                        className="image-preview-overlay"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsPreviewOpen(false)}
                    >
                        <motion.div
                            className="preview-content"
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <button className="close-preview" onClick={() => setIsPreviewOpen(false)}>
                                <X size={32} />
                            </button>
                            <img src={userData.profileImg} alt="Profile Full" className="full-profile-img" />
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default Account;
