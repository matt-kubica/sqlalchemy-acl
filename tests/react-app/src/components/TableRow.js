import React from "react";

const TableRow = ({ contents }) => {
  var fields = [];
  Object.keys(contents).forEach((key) => fields.push(contents[key] + " | "));
  return <li>{fields}</li>;
};

export default TableRow;
