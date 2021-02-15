import React from "react";

const SelectTable = ({ setTable }) => {
  return (
    <select
      className="width custom-select"
      onChange={(e) => setTable(e.target.value)}
    >
      <option value="/exemplary-object">Exemplary</option>
      <option value="/contents">Contents</option>
      <option value="/boxes">Boxes</option>
      <option value="/articles">Articles</option>
      <option value="/orders">Orders</option>
      <option value="/customers">Customers</option>
      <option value="/salaries">Salaries</option>
    </select>
  );
};

export default SelectTable;
