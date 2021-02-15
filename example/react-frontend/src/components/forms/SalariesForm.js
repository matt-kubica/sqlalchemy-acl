import React, { useState, useEffect } from "react";

const SalariesForm = ({ handleAddition, setBody }) => {
  const [id, setId] = useState(0);
  const [name, setName] = useState("");
  const [salary, setSalary] = useState("");

  useEffect(() => {
    setBody(JSON.stringify({ id, name, salary }));
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
          placeholder="Salary"
          onChange={(e) => setSalary(e.target.value)}
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

export default SalariesForm;
