import React from "react";
import TableRow from "./TableRow";

const Table = ({ name, data }) => {
  var keys = [];
  Object.keys(data[0]).forEach((key) => keys.push(key + " | "));
  return (
    <ul className="list">
      <li className="list-title">{name}</li>
      <li> {keys}</li>
      <li>
        <ul>
          {data.map((row) => {
            return <TableRow key={row.id} contents={row} />;
          })}
        </ul>
      </li>
    </ul>
  );
};

export default Table;
