import React from "react";
import TableRow from "./TableRow";

const Table = ({ name, data }) => {
  return (
    <ul className="list">
      <li>
        <h1>{name}</h1>
        <ul className="list">
          {data.map((row) => {
            return <TableRow key={row.id} contents={row} />;
          })}
        </ul>
      </li>
    </ul>
  );
};

export default Table;
