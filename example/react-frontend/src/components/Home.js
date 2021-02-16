import React, { useEffect, useState } from "react";
import { api } from "../services/api.js";

const Home = () => {
  const [message, setMessage] = useState("");

  useEffect(() => {
    api
      .get("/hello", {
        headers: {
          Authorization:
            "Bearer " + JSON.parse(sessionStorage.getItem("token")).token,
        },
      })
      .then((res) => setMessage(res.data.msg))
      .catch((error) => window.alert(error));
  });

  return (
    <div className="auth-wrapper">
      <div className="auth-inner">
        <h1>{message}</h1>
      </div>
    </div>
  );
};

export default Home;
