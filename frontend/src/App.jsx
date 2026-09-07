import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./login";
import Signin from "./signin";
import FarmDetails from "./FarmDetails";
import Home from "./Home";
import MyFarms from "./MyFarms";
import ProductionSummary from "./ProductionSummary";
import LiveDetection from "./LiveDetection";
import Account from "./Account";
import EditFarm from "./EditFarm";
import FarmSelectionForSummary from "./FarmSelectionForSummary";
import PredictionGraph from "./PredictionGraph";
import EditProfile from "./EditProfile";
import Notification from "./Notification";
import Summary from "./Summary";
import BatchImages from "./BatchImages";



import thumb1 from "./assets/farm_thumb_1_1771671329281.png";
import thumb2 from "./assets/farm_thumb_2_1771671341783.png";
import thumb3 from "./assets/farm_thumb_3_1771671357060.png";
import { isPrimaryPointer } from "framer-motion";

function App() {
  const [userData, setUserData] = useState({
    name: "",
    email: "",
    profileImg: null
  });
   const [accumulatedResults, setAccumulatedResults] = useState({ classA: 0, classB: 0, classC: 0, totalWeight: 0, fruitName: "",image:"",confidence:0 });

  
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signin" element={<Signin />} />
        <Route path="/farm-details" element={<FarmDetails/>} />
        <Route path="/home" element={<Home userData={userData} />} />
        <Route path="/my-farms" element={<MyFarms/>} />
        <Route path="/farm-selection-summary" element={<FarmSelectionForSummary />} />
        <Route path="/production-summary/:farmId" element={<ProductionSummary />} />
        <Route path="/prediction-graph" element={<PredictionGraph />} />
        <Route path="/live-detection" element={<LiveDetection />} />
        <Route path="/account" element={<Account userData={userData} setUserData={setUserData} />} />
        <Route path="/edit-farm/:id" element={<EditFarm />} />
        <Route path="/edit-profile" element={<EditProfile setUserData={setUserData} />} />
        <Route path="/notification" element={<Notification />} />
        <Route path="/summary" element={<Summary setAccumulatedResults={setAccumulatedResults}/>} />
        <Route path="/batch-images/:batchId" element={<BatchImages />} />
 
      </Routes>
    </BrowserRouter>
  );
}









export default App;
