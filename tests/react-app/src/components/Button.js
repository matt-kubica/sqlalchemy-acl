import React from "react";

const Button = ({ label, onClick }) => {
  return (
    <div className="auth-inner">
      <button onClick={onClick}>{label}</button>
    </div>
  );
};

export default Button;
