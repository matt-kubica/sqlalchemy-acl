import React, { useState } from "react";
import { api } from "../services/api.js";

const Signup = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [access_level, setAccessLevel] = useState("");

  function handleSubmit() {
    api
      .post("/register", {
        username: username,
        email: email,
        password: password,
        access_level: access_level,
      })
      .then((res) => window.alert(res))
      .catch((error) => window.alert(error));
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-inner">
        <form onSubmit={handleSubmit}>
          <h3>Sign Up</h3>
          <div className="form-group">
            <label>Username</label>
            <input
              onChange={(e) => setUsername(e.target.value)}
              type="text"
              className="form-control"
              placeholder="Username"
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              className="form-control"
              placeholder="Email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              className="form-control"
              placeholder="Password"
            />
          </div>

          <div className="form-group">
            <label>Access Level</label>
            <input
              onChange={(e) => setAccessLevel(e.target.value)}
              type="text"
              className="form-control"
              placeholder="Access Level"
            />
          </div>

          <button type="submit" className="btn btn-primary btn-block">
            Sign Up
          </button>
          <p>
            <a href="/sign-in">Already have an account?</a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Signup;
