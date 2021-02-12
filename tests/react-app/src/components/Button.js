import React from "react";

const Button = ({ onClick }) => {
  return (
    <div className="auth-inner">
      <button onClick={onClick}>Get available rows</button>
    </div>
  );
};

export default Button;
