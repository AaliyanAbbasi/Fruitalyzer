import React, { useState, useEffect } from "react";
import { Home as HomeIcon, Bell as NotificationIcon, User } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "./Home.css";

import productionImg from "./assets/production_summary_bg_1771663681087.png";
import detectionImg from "./assets/live_detection_bg_1771663701144.png";
import farmsImg from "./assets/view_farms_bg_1771663715666.png";

const Home = () => {
    const navigate = useNavigate();
    const [showNav, setShowNav] = useState(false);
    const [userName, setUserName] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [userFarms, setUserFarms] = useState([]);

    useEffect(() => {
        const fetchUserData = async () => {
            const userId = localStorage.getItem("user_id");
            if (userId) {
                try {
                    const res = await fetch(`/get_landlord_by_id/${userId}`);
                    if (res.ok) {
                        const data = await res.json();
                        if (data.name) {
                            setUserName(data.name);
                        }
                    }
                } catch (error) {
                    console.error("Error fetching user name:", error);
                }
            }
        };
        fetchUserData();
    }, []);

    const fetchFarms = async () => {
        try {
            const userId = Number(localStorage.getItem("user_id"));
            const res = await fetch("/get_all_farms_of_landlord", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ landlord_id: userId }),
            });
            const data = await res.json();
            if (res.ok) {
                setUserFarms(data);
            }
        } catch (err) {
            console.error("Failed to fetch farms:", err);
        }
    };

    const handleBannerClick = (banner) => {
        if (banner.title === "Live Detection") {
            fetchFarms();
            setIsModalOpen(true);
        } else if (banner.path) {
            navigate(banner.path);
        }
    };

    useEffect(() => {
        const handleScroll = () => {
            const isBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 50;
            setShowNav(isBottom);
        };

        window.addEventListener("scroll", handleScroll);
        // Initial check in case content is short
        handleScroll();

        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const banners = [
        {
            title: "Production Summary",
            subtitle: "View your farm's performance",
            img: productionImg,
            path: "/farm-selection-summary"
        },
        {
            title: "Live Detection",
            subtitle: "Real-time monitoring",
            img: detectionImg,
            path: "/live-detection"
        },
        {
            title: "View Farms",
            subtitle: "Manage your orchards",
            img: farmsImg,
            path: "/my-farms"
        }
    ];



    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.2
            }
        }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: {
                type: "spring",
                stiffness: 100
            }
        }
    };

    return (
        <motion.div
            className="home-container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <h1 className="home-title">Hello {userName}!</h1>
            

            <p className="home-subtitle" variants={itemVariants}>
                <span className="yellow">What You </span>
                <span className="green">Want To Go </span>
                <span className="yellow">With Today?</span>
            </p>

            <div className="banner-list">
                {banners.map((banner, index) => (
                    <motion.div
                        key={index}
                        className="banner-item"
                        style={{ backgroundImage: `url(${banner.img})` }}
                        variants={itemVariants}
                        whileHover={{ scale: 1.02, y: -5 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleBannerClick(banner)}
                    >

                        <div className="banner-overlay">
                            <h2>{banner.title}</h2>
                            <p>{banner.subtitle}</p>
                        </div>
                    </motion.div>
                ))}
            </div>

            <AnimatePresence>
                {isModalOpen && (
                    <motion.div
                        className="modal-overlay"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsModalOpen(false)}
                    >
                        <motion.div
                            className="farm-modal"
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <h2>Select Farm</h2>
                            <p>Choose a farm to start live detection</p>

                            <div className="modal-farms-list">
                                {userFarms.length > 0 ? (
                                    userFarms.map(farm => (
                                        <div
                                            key={farm.id}
                                            className="modal-farm-item"
                                            onClick={() => {
                                                setIsModalOpen(false);
                                                navigate("/live-detection", { state: { farmId: farm.id, farmName: farm.name } });
                                            }}
                                        >
                                            <div className="farm-icon">🚜</div>
                                            <div className="farm-details">
                                                <h3>{farm.name}</h3>
                                                <p>{farm.city}</p>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <p className="no-farms">No farms found. Please add a farm first.</p>
                                )}
                            </div>

                            <button className="close-modal-btn" onClick={() => setIsModalOpen(false)}>
                                Cancel
                            </button>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            <AnimatePresence>
                {showNav && (
                    <motion.nav
                        className="bottom-nav"
                        initial={{ y: 100, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 100, opacity: 0 }}
                        transition={{ type: "spring", stiffness: 100, damping: 15 }}
                    >
                        <div
                            className="nav-item active"
                            whileTap={{ scale: 0.95 }}
                        >
                            <HomeIcon size={26} />
                            <span>Home</span>
                        </div>
                        <div
                            className="nav-item"
                            onClick={() => navigate("/notification")}
                            whileTap={{ scale: 0.95 }}
                        >
                            <div className="icon-wrapper">
                                <NotificationIcon size={26} />
                                <span className="notification-badge">9</span>
                            </div>
                            <span>Notification</span>
                        </div>
                        <div
                            className="nav-item"
                            onClick={() => navigate("/account")}
                            whileTap={{ scale: 0.95 }}
                        >
                            <User size={26} />
                            <span>Account</span>
                        </div>
                    </motion.nav>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default Home;
