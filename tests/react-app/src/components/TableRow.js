import React from "react";

const TableRow = ({ contents }) => {
  return (
    <li>
      {contents.id + " "}
      {contents.integer_field + " "}
      {contents.string_field}
    </li>
  );
};

export default TableRow;
