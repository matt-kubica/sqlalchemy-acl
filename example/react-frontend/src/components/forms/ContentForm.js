import React, { useState, useEffect } from "react";

const ContentForm = ({ handleAddition, setBody }) => {
  const [id, setId] = useState(0);
  const [box_id, setBoxId] = useState(0);
  const [chocolate_name, setChocName] = useState("");
  const [quantity, setQuantity] = useState(0);

  useEffect(() => {
    setBody(JSON.stringify({ id, box_id, chocolate_name, quantity }));
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
          placeholder="Box ID"
          onChange={(e) => setBoxId(e.target.value)}
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="Chocolate name"
          onChange={(e) => setChocName(e.target.value)}
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

export default ContentForm;
