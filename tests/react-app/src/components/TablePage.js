import React, { useState } from "react";
import Table from "./Table";
import Button from "./Button";
import { api } from "../services/api.js";

const TablePage = () => {
  const [data, setData] = useState([]);

  if (data.length === 0) {
    return (
      <div className="auth-wrapper">
        <Button onClick={handleClick} />
      </div>
    );
  }

  function handleClick() {
    setData([{ att1: "value" }]);
    api
      .get("/exemplary-object", {
        headers: {
          Authorization:
            "Bearer " + JSON.parse(sessionStorage.getItem("token")).token,
        },
      })
      .then((res) => {
        setData(res.data);
      });
  }

  return (
    <div className="table-wrapper">
      <Table name={"Mati"} data={data} />
    </div>
  );
};

export default TablePage;
