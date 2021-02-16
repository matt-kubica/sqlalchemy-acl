import React, { useState } from "react";
import Table from "./Table";
import ActionWindow from "./ActionWindow";

const TablePage = () => {
  const [data, setData] = useState([]);
  const [tablename, setTableName] = useState("");

  if (data.length === 0) {
    return (
      <div className="auth-wrapper">
        <ActionWindow setData={setData} setTableName={setTableName} />
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <Table
        name={tablename.charAt(1).toUpperCase() + tablename.slice(2)}
        data={data}
      />
    </div>
  );
};

export default TablePage;
