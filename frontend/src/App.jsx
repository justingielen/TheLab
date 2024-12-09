import "./App.css";
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import Welcome from "./components/Welcome";
import SideBar from "./components/SideBar";

function App() {
  return (
    <Router>
      <div className="AppLayout">
        {/* Persistent NavBar */}
        <NavBar />
        <div className="container-fluid">
          <div className="row">
            {/* SideBar */}
            <div className="col-md-4">
              <SideBar />
            </div>

            {/* Main Content*/}
            <div className="col-md-8">
              <Routes>
                <Route path="/" element={<Welcome />} />
                {/* Other Routes*/}
              </Routes>
            </div>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
