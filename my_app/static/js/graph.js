// my_app/static/js/graph.js

function displayTables() {
 const tables = {
        "lost": [
            ["date", "datetime", "дата и время проведения потерь"],
            ["warehouse_id", "integer", "идентификатор склада"],
            ["product_id", "integer", "идентификатор товара"],
            ["item_id", "integer", "идентификатор статьи потерь. Например, списание по сроку годности - 146"],
            ["quantity", "decimal", "потери в количестве"],
            ["amount", "decimal", "сумма потерь"]
        ],
        "order_line": [
            ["order_id", "integer", "идентификатор заказа"],
            ["date", "datetime", "дата и время создания заказа"],
            ["warehouse_id", "integer", "идентификатор склада"],
            ["product_id", "integer", "идентификатор товара"],
            ["price", "decimal", "цена продажи"],
            ["regular_price", "decimal", "регулярная цена"],
            ["cost_price", "decimal", "цена в себестоимости"],
            ["quantity", "decimal", "количество проданных единиц товара"],
            ["paid_amount", "decimal", "сумма продаж"]
        ],
        "orders": [
            ["order_id", "integer", "идентификатор заказа"],
            ["warehouse_id", "integer", "идентификатор склада"],
            ["user_id", "integer", "идентификатор клиента"],
            ["date", "datetime", "дата и время создания заказа"],
            ["paid_amount", "decimal", "сумма заказа"],
            ["quantity", "decimal", "количество единиц товаров в заказе"]
        ],
        "products": [
            ["product_id", "integer", "идентификатор товара"],
            ["name", "varchar", "наименование товара"],
            ["group1", "varchar", "группа товаров 1 уровня"],
            ["group2", "varchar", "группа товаров 2 уровня"],
            ["group3", "varchar", "группа товаров 3 уровня"],
            ["weight", "decimal", "вес товара"],
            ["shelf_life", "integer", "срок годности товара в днях"]
        ],
        "warehouses": [
            ["warehouse_id", "integer", "идентификатор склада"],
            ["name", "varchar", "наименование склада"],
            ["city", "varchar", "город"],
            ["date_open", "date", "дата открытия склада"],
            ["date_close", "date", "дата закрытия склада"]
        ]
        };

    const container = document.getElementById('canvas');
    Object.keys(tables).forEach(table => {
        const tableDiv = document.createElement('div');
        tableDiv.style.padding = '10px';
        tableDiv.style.backgroundColor = '#f8f9fa';
        tableDiv.style.border = '1px solid #ced4da';
        tableDiv.style.borderRadius = '4px';
        tableDiv.style.marginBottom = '10px';

        const titleDiv = document.createElement('div');
        titleDiv.style.fontWeight = 'bold';
        titleDiv.style.marginBottom = '5px';
        titleDiv.innerText = table;
        tableDiv.appendChild(titleDiv);

        tables[table].forEach(col => {
            const colDiv = document.createElement('div');
            colDiv.innerText = `${col[0]}: ${col[1]}`;
            tableDiv.appendChild(colDiv);
        });

        container.appendChild(tableDiv);
    });
}

// Display the tables once the document is ready
document.addEventListener('DOMContentLoaded', displayTables);
