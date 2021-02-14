import React from "react";
import TableRow from "./TableRow";

const Table = ({ name, data }) => {
  var keys = [];
  Object.keys(data[0]).forEach((key) => keys.push(key + " | "));
  return (
    <ul className="list">
      <li key="Title" className="list-title">
        {name}
      </li>
      <li key="Keys"> {keys}</li>
      <li key="RowList">
        <ul key="Rows">
          {data.map((row) => {
            return <TableRow key={row.id} contents={row} />;
          })}
        </ul>
      </li>
    </ul>
  );
};

export default Table;
