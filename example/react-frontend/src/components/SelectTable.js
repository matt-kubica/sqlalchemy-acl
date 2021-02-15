import React from "react";

const SelectTable = ({ setTable, setTableName }) => {
  return (
    <select
      className="width custom-select"
      onChange={(e) => {
        setTable(e.target.value);
        setTableName(e.target.value);
      }}
    >
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
