import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";


const Login = () => {
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const [email, setemail] = useState("");
    const [password, setpassword] = useState("")

    const handlelogin = async () => {
        if (email == "" || password == "") {
            alert("Please fill in all fields");
            return;
        }


        try {
            const res = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                }),
            });

            const data = await res.json();

            if (res.status === 200) {
                localStorage.setItem("user_id", data.user_id);
                navigate("/home");
            } else {
                alert(data.detail || data.error || "Login failed");
            }
        } catch (err) {
            console.log(err);
            alert("Server not responding");
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h1 className="title">Hello!</h1>
                <p className="subtitle">Welcome back</p>

                <div className="input-group">
                    <label>Email</label>
                    <input type="email"
                        placeholder="Enter email"
                        value={email}
                        onChange={(e) => setemail(e.target.value)} />
                </div>

                <div className="input-group">
                    <label>Password</label>
                    <div className="password-box">
                        <input
                            type={showPassword ? "text" : "password"}
                            placeholder="Enter password"
                            value={password}
                            onChange={(e) => setpassword(e.target.value)}
                        />
                        <span
                            className="toggle"
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            👁
                        </span>
                    </div>
                </div>

                <div className="forgot">Forgot password?</div>

                <button className="login-btn" onClick={handlelogin}>Login
                </button>


                <p className="signup-text">
                    Don't have an account?
                    <span onClick={() => navigate("/signin")}> Sign up</span>
                </p>
            </div>
        </div>
    );
};


export default Login;
