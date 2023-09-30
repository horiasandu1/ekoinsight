import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ReactDOM from "react-dom/client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import SignIn from "./pages/SignIn";
import Home from "./pages/Home";

export default function App() {
  return (
    <GoogleOAuthProvider clientId="322046876890-rmv68tp2jh1ia7um7ija4iqbsds12k7j.apps.googleusercontent.com">
      <BrowserRouter>
        <Routes>
          <Route path="/">
            <Route index element={<Home />}></Route>
            <Route path="signin" element={<SignIn />}></Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </GoogleOAuthProvider>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <>
    <App />
  </>
);
