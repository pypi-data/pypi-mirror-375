POST_RESOURCE_ID_DESCRIPTION = """# Add data into resource.

Add the corresponding data into the named Resource.

Rules (`/{resource}/{id}`):  
- If resource does not exists it will be added.
- If the ID resource does not exists it will be added.
- If the ID resource exist it will be updated.
- The body structure<sup>*</sup> should be a valid JSON (`{ key: value, keyN: valueN }`) with any number of items.
- The structure shold have at least one **ID-like** attribute (example for `products` resource: `id`, `productId`, `idProduct`).
- Other them the ID-like attributes are not validated.

\\* Simple sample body structure and data:  
```json
{
  "brand": "Adidas",
  "color": "Black",
  "id": 1,
  "image": "http://products.net/img/",
  "price": 40,
  "reviewScore": 1.0431592108,
  "size": "XL",
  "title": "Dress"
}
```
or:  
```json
{
  "title": "Dress",
  "size": "XL",
  "reviewScore": 1.0431592108,
  "productId": 1,
  "price": 40,
  "image": "http://products.net/img/",
  "color": "Black",
  "brand": "Adidas"
}
```

"""

GET_RESOURCE_ID_DESCRIPTION = """# Get Resource ID Data

Get the corresponding data for the **first** attribute with **ID-like** (e.g: `id`, `ceoUserId`, `idProduct`) found in the data structure<sup>*</sup>.

| status | results
| ------ | -------
|  200   | OK.
|  404   | The `resource` requested not found.
|  404   | The `resource` requested has not an **ID-like** attribute.
|  404   | Data not found for the `resource`/`id`. *It only checks for the first **ID-like** atribute.*

\\* Let's suppose this sample structure and data:  
```json
{
  "stoke-exchange": [
    {
      "company": "Chuchu e Melão S/A",
      "city": "Belo Horizonte",
      "ceoUserId": "99273502-9448-4197-abc4-422d4c792264",
      "state": "Minas Gerais",
      "id": 19,
      "country": "Brasil",
      "postcode": 40256,
      "idProduct": 19,
      "priceTag": 45593820,
      "shareValue": 617.00
    }
  ]
}
```

So, for the following requests:

1. `GET /stoke-exchange/17`: it is not found, `ceoUserId == 17` does not matches.
2. `GET /stoke-exchange/19`: it is not found, `ceoUserId == 19` does not matches.
3. `GET /stoke-exchange/99273502-9448-4197-abc4-422d4c792264`: **it is found**, `ceoUserId == "99273502-9448-4197-abc4-422d4c792264"` matches.

And the other way round for the structure and data also works, e.g.:  
```json
{
  "stoke-exchange": [
    {
      "company": "Chuchu e Melão S/A",
      "city": "Belo Horizonte",
      "idProduct": 19,
      "state": "Minas Gerais",
      "id": 17,
      "country": "Brasil",
      "ceoUserId": "99273502-9448-4197-abc4-422d4c792264",
      "postcode": 40256,
      "priceTag": 45593820,
      "shareValue": 617.00
    }
  ]
}
```

Requests:
1. `GET /stoke-exchange/99273502-9448-4197-abc4-422d4c792264`: it is not found.
2. `GET /stoke-exchange/17`: it is not found.
3. `GET /stoke-exchange/19`: **it is found**, `idProduct == 19` matches.

"""
