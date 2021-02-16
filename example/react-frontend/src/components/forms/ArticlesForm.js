import React, { useState, useEffect } from "react";

const ArticlesForm = ({ handleAddition, setBody }) => {
  const [id, setId] = useState(0);
  const [order_id, setOrder] = useState("");
  const [box_id, setBox] = useState("");
  const [quantity, setQuantity] = useState("");

  useEffect(() => {
    setBody(JSON.stringify({ id, order_id, box_id, quantity }));
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
          placeholder="Order ID"
          onChange={(e) => setOrder(e.target.value)}
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="Box ID"
          onChange={(e) => setBox(e.target.value)}
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="Quantity"
          onChange={(e) => setQuantity(e.target.value)}
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

export default ArticlesForm;
