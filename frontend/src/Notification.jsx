import React, { useState, useEffect } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import "./Notification.css";
import { ChevronLeft } from "lucide-react";


const Notification = () => {
    const navigate = useNavigate();
    const[username, setUsername] = useState("");
useEffect(()=>{
    const fetchdata = async () => {
        const userId=localStorage.getItem("user_id");
        if(userId){
            try{
                const res=await fetch(`/get_landlord_by_id/${userId}`);
                if(res.ok){
                    const data =await res.json();
                    if(data.name){
                        setUsername(data.name);
                    }
                }
            }
        
        catch(error){
            console.error("error fetching name")
        }
    }
        

    };fetchdata();
},[]);
 
    return (
        <div className="notification-container">
            <header className="notification-header">
                <button className='back-button' onClick={() => navigate('/home')}>
                    <ChevronLeft size={32} />
                </button>
                <h1 className='notification-title'>Notification of {username}</h1>
            </header>
            <div className="notification-content">
                {/*  */}
                <div className="empty-notifications">
                    <p>No new notifications</p>
                </div>
            </div>
        </div>
    );
};
export default Notification;