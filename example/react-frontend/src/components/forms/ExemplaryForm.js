import React, { useState, useEffect } from "react";

const ExemplaryForm = ({ handleAddition, setBody }) => {
  const [id, setId] = useState(0);
  const [string_field, setString] = useState("");
  const [integer_field, setInteger] = useState(0);

  useEffect(() => {
    setBody(
      JSON.stringify({
        id: id,
        string_field: string_field,
        integer_field: integer_field,
      })
    );
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
          placeholder="String"
          onChange={(e) => setString(e.target.value)}
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          className="form-control"
          placeholder="Integer"
          onChange={(e) => setInteger(e.target.value)}
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

export default ExemplaryForm;
