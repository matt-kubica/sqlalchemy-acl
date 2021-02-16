import React from "react";
import ArticlesForm from "./ArticlesForm";
import BoxesForm from "./BoxesForm";
import ContentForm from "./ContentForm";
import CustomersForm from "./CustomersForm";
import OrdersForm from "./OrdersForm";
import SalariesForm from "./SalariesForm";
import ExemplaryForm from "./ExemplaryForm";

const FormController = ({ to_table, setBody, handleAddition }) => {
  switch (to_table) {
    case "/articles":
      return <ArticlesForm handleAddition={handleAddition} setBody={setBody} />;
    case "/boxes":
      return <BoxesForm handleAddition={handleAddition} setBody={setBody} />;
    case "/contents":
      return <ContentForm handleAddition={handleAddition} setBody={setBody} />;
    case "/customers":
      return (
        <CustomersForm handleAddition={handleAddition} setBody={setBody} />
      );
    case "/orders":
      return <OrdersForm handleAddition={handleAddition} setBody={setBody} />;
    case "/salaries":
      return <SalariesForm handleAddition={handleAddition} setBody={setBody} />;
    case "/exemplary-object":
      return (
        <ExemplaryForm handleAddition={handleAddition} setBody={setBody} />
      );
    default:
      return <div>Default Option</div>;
  }
};

export default FormController;
