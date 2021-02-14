import React from "react";

const Button = ({ label, onClick }) => {
  return (
    <div>
      <button className="btn btn-primary" onClick={onClick}>
        {label}
      </button>
    </div>
  );
};

export default Button;
