import React, { useState } from "react";
import Table from "./Table";
import ActionWindow from "./ActionWindow";

const TablePage = () => {
  const [data, setData] = useState([]);

  if (data.length === 0) {
    return (
      <div className="auth-wrapper">
        <ActionWindow setData={setData} />
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <Table name={"Mati"} data={data} />
    </div>
  );
};

export default TablePage;
