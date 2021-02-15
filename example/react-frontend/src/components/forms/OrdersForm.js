import React, { useState, useEffect } from "react";

const CustomersForm = ({ handleAddition, setBody }) => {
  const [id, setId] = useState(0);
  const [customer_id, setCustomerId] = useState("");
  const [order_date, setOrderDate] = useState("");

  useEffect(() => {
    setBody(JSON.stringify({ id, customer_id, order_date }));
  });

  return (
    <form>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="ID"
          onChange={(e) => setId(e.target.value)}
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="Customer ID"
          onChange={(e) => setCustomerId(e.target.value)}
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="Order Date"
          onChange={(e) => setOrderDate(e.target.value)}
        />
      </div>
      <button
        type="submit"
        className="btn btn-primary"
        onClick={handleAddition}
      >
        Add row
      </button>
    </form>
  );
};

export default CustomersForm;
