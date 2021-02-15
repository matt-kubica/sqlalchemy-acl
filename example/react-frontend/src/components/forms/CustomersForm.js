import React, { useState, useEffect } from "react";

const CustomersForm = ({ handleAddition, setBody }) => {
  const [id, setId] = useState(0);
  const [name, setName] = useState("");
  const [phone_number, setPhone] = useState("");

  useEffect(() => {
    setBody(JSON.stringify({ id, name, phone_number }));
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
          placeholder="Phone"
          onChange={(e) => setPhone(e.target.value)}
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
