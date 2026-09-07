import React, { useState } from "react";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./signin.css";

const Signin = () => {
    const [showPassword, setShowPassword] = useState(false);
    const [showRePassword, setShowRePassword] = useState(false);

    // 👇 NEW STATES
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [rePassword, setRePassword] = useState("");

    const navigate = useNavigate();

    const handleSignup = async () => {
        if (!name || !email || !password || !rePassword) {
            alert("Please fill all fields");
            return;
        }

        if (password !== rePassword) {
            alert("Passwords do not match");
            return;
        }

        try {
            const res = await fetch("/sign_up", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password,
                }),
            });

            const data = await res.json();

            if (res.status === 200) {
                alert("Signup successful");
                // login page
            } else {
                alert(data.detail || data.error || "Signup failed");
            }
        } catch (error) {
            console.log(error);
            alert("Server error");
        }
    };

    return (
        <div className="signin-container">
            <div className="signin-card">
                <h1 className="title">Welcome!</h1>

                {/* NAME */}
                <div className="input-group">
                    <label>Name</label>
                    <input
                        type="text"
                        placeholder="Enter Full Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                    />
                </div>

                {/* EMAIL */}
                <div className="input-group">
                    <label>Email</label>
                    <div className="input-wrapper">
                        <Mail size={20} />
                        <input
                            type="email"
                            placeholder="example@gmail.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                </div>

                {/* PASSWORD */}
                <div className="input-group">
                    <label>Password</label>
                    <div className="input-wrapper">
                        <Lock size={20} />
                        <input
                            type={showPassword ? "text" : "password"}
                            placeholder="********"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <button type="button" onClick={() => setShowPassword(!showPassword)}>
                            {showPassword ? <Eye size={20} /> : <EyeOff size={20} />}
                        </button>
                    </div>
                </div>

                {/* RE PASSWORD */}
                <div className="input-group">
                    <label>Re-Enter Password</label>
                    <div className="input-wrapper">
                        <Lock size={20} />
                        <input
                            type={showRePassword ? "text" : "password"}
                            placeholder="********"
                            value={rePassword}
                            onChange={(e) => setRePassword(e.target.value)}
                        />
                        <button type="button" onClick={() => setShowRePassword(!showRePassword)}>
                            {showRePassword ? <Eye size={20} /> : <EyeOff size={20} />}
                        </button>
                    </div>
                </div>

                {/* BUTTON */}
                <button className="signin-btn" onClick={handleSignup}>
                    Sign up
                </button>
            </div>
        </div>
    );
};

export default Signin;