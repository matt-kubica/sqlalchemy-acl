import React, { useState, useEffect } from "react";

const BoxesForm = ({ handleAddition, setBody }) => {
  const [id, setId] = useState(0);
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");

  useEffect(() => {
    setBody(JSON.stringify({ id, name, price, stock }));
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
          placeholder="Name"
          onChange={(e) => setName(e.target.value)}
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="Price"
          onChange={(e) => setPrice(e.target.value)}
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="Stock"
          onChange={(e) => setStock(e.target.value)}
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

export default BoxesForm;
