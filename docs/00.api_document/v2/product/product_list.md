**Product information**
----

* **URL**

    /products/<hub_id>/time/<time_type>

* **Method:**

    `GET`

*  **URL Params**

    hub_id: central-1, pudong-2, time_type: morning-1, lunch-2, dinner=3

   **Required:**

   `hub_id=[integer]`
   
   `time_type=[integer]`

* **Data Params**

    None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ "code": 200, "message": "success" }`

* **Error Response:**

  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** `{ "code": 401, "message": "Authentication failed", "err_code" : 1007 }`

* **Sample Call:**

    ```
    
    ```
    
* **Notes:**
    
    Authentication information is an option.

**Product detail**
----

* **URL**

    /products/<product_id>/detail

* **Method:**

    `GET`

*  **URL Params**

   **Required:** 
   
   `product_id=[integer]`

* **Data Params**

    None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ "code": 200, "message": "success" }`

* **Error Response:**

  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** `{ "code": 401, "message": "Authentication failed", "err_code" : 1007 }`

* **Sample Data:**

    ```
    "message": "success",
    "code": 200,
    "products": [
        {
            "id": 56,
            "hub": 1,
            "menu": {
                "id": 53,
                "restaurant": {
                    "id": 12,
                    "name": "WINE",
                    "chef": "Wine chef",
                    "introduce_image": "",
                    "award_info": []
                },
                "name": "Bicycle 2015",
                "cooking_materials": "Tempranillo",
                "image_main": "restaurant/wine/menu/7_Bicycle2015/main/img_wine_main_07_Bicycle_2015.png",
                "image_detail": "restaurant/wine/menu/7_Bicycle2015/detail/img_wine_detail_07_Bicycle_2015.png",
                "image_sub": "restaurant/wine/menu/7_Bicycle2015/sub/img_wine_972X680_07_Bicycle_2015.png",
                "image_thumbnail": "restaurant/wine/menu/7_Bicycle2015/thumbnail/img_wine_thumb_07_Bicycle_2015.png",
                "description": [
                    "Superb intensity on the nose"
                ],
                "image_package": "",
                "prep_tips": {},
                "prep_plating_thumbnail": "",
                "prep_plating_url": "",
                "ingredients": [],
                "nutrition": [],
                "notices": [],
                "subs_contents": [],
                "media_contents": [],
                "image_detail_list": [
                    "restaurant/wine/Drinkuaidi/menu/7_Bicycle2015/detail/img_wine_detail_07_Bicycle_2015.png"
                ],
                "review_statics": {
                    "review_count_postfix": "",
                    "review_count": 0,
                    "average_point": 0
                }
            },
            "list_index": 49,
            "type": 5,
            "price": 27,
            "price_discount": 0,
            "price_discount_event": false,
            "price_unit": 0,
            "category": [],
            "status": 1,
            "sales_time": 3,
            "type_name": "Wine",
            "type_index": 5,
            "status_label": "ORDER FOR DINNER",
            "badge": []
        },
    "page_size": 5,
    "customer_reviews": [],
    "expert_review": [
        {
            "created_date": "2018-04-27",
            "expert_job": "Chef",
            "expert_name": "Jiae Choi",
            "expert_image": "experts/profile_2.png",
            "expert_comment": [
                "Vegetarian-friendly salad. Chickpea ..."
            ]
        }
    "total_count": 0,
        "product": {
        "id": 125,
        "hub": 1,
        "menu": {
            "id": 66,
            "restaurant": {
                "id": 7,
                "name": "Via Stelle",
                "chef": "Hawa Song, Jiae Choi",
                "introduce_image": "restaurant/viastelle/img_chef_viastelle.png",
                "award_info": []
            },
            "name": "Egyptian Hummus",
            "cooking_materials": "hummus, feta cheese, cucumber, red crunchy chickpeas, Lime yogurt dressing",
            "image_main": "fresh/menu/egyptian/img_main_egyptianhummus.png",
            "image_detail": "fresh/menu/egyptian/img_detail_egyptianhummus_01.png",
            "image_sub": "fresh/menu/egyptian/img_680_egyptianhummus.png",
            "image_thumbnail": "fresh/menu/egyptian/img_thumb_egyptianhummus.png",
            "description": [
                "Salad with a combination of."
            ],
            "image_package": "",
            "prep_tips": {},
            "prep_plating_thumbnail": "",
            "prep_plating_url": "",
            "ingredients": [
                {
                    "name": "Kale",
                    "quantity": ""
                },
                {
                    "name": "Spinach",
                    "quantity": ""
                },
                {
                    "name": "Romaine",
                    "quantity": ""
                },
                {
                    "name": "Frisee",
                    "quantity": ""
                },
                {
                    "name": "Chickpea",
                    "quantity": ""
                },
                {
                    "name": "Sesame paste",
                    "quantity": ""
                },
                {
                    "name": "Olive oil",
                    "quantity": ""
                },
                {
                    "name": "Lemon juice",
                    "quantity": ""
                },
                {
                    "name": "Salt",
                    "quantity": ""
                },
                {
                    "name": "Feta cheese",
                    "quantity": ""
                },
                {
                    "name": "Cucumber",
                    "quantity": ""
                },
                {
                    "name": "Yogurt",
                    "quantity": ""
                },
                {
                    "name": "Lime",
                    "quantity": ""
                },
                {
                    "name": "Honey",
                    "quantity": ""
                },
                {
                    "name": "Red onion",
                    "quantity": ""
                },
                {
                    "name": "Tomato",
                    "quantity": ""
                }
            ],
            "nutrition": [
                {
                    "name": "Calories",
                    "quantity": "545kcal"
                },
                {
                    "name": "Total Fat",
                    "quantity": "27g"
                },
                {
                    "name": "    Saturated Fat",
                    "quantity": "3g"
                },
                {
                    "name": "Cholesterol ",
                    "quantity": "27mg"
                },
                {
                    "name": "Sodium ",
                    "quantity": "1227mg"
                },
                {
                    "name": "Carbohydrate ",
                    "quantity": "45g"
                },
                {
                    "name": "Protein ",
                    "quantity": "38g"
                },
                {
                    "name": "Vitamin A ",
                    "quantity": "685μg"
                },
                {
                    "name": "Vitamin C ",
                    "quantity": "65mg"
                },
                {
                    "name": "Calcium ",
                    "quantity": "601mg"
                },
                {
                    "name": "Iron ",
                    "quantity": "10mg"
                }
            ],
            "notices": [],
            "subs_contents": [],
            "media_contents": [
                {
                    "media_title": {
                        "underline": false,
                        "bold": false,
                        "text": ""
                    },
                    "media_content": [
                        {
                            "type": "image",
                            "content": "fresh/menu/how.png"
                        }
                    ],
                    "section_title": [
                        {
                            "underline": false,
                            "bold": false,
                            "text": "HOW TO"
                        },
                        {
                            "underline": false,
                            "bold": true,
                            "text": "EAT"
                        }
                    ],
                    "desc_title": {
                        "underline": true,
                        "bold": true,
                        "text": ""
                    },
                    "description": [
                        "Take the salad dressing container out.",
                        "Shake the dressing to mix well, pour onto the salad.",
                        "Close the lid and shake well, or use spoon and fork to mix.",
                        "Use spoon and fork to enjoy chop salad."
                    ]
                },
                {
                    "media_title": {
                        "underline": true,
                        "bold": true,
                        "text": "CHOP SALAD IN ACTION"
                    },
                    "media_content": [
                        {
                            "type": "video",
                            "content": "fresh/vid/chop_01.mp4",
                            "thumbnail": "fresh/vid/chop_01.png"
                        }
                    ],
                    "section_title": [],
                    "desc_title": {
                        "underline": false,
                        "bold": false,
                        "text": ""
                    },
                    "description": []
                }
            ],
            "image_detail_list": [
                "fresh/menu/egyptian/img_detail_egyptianhummus_01.png",
                "fresh/menu/egyptian/img_detail_egyptianhummus_02.png",
                "fresh/menu/egyptian/img_detail_egyptianhummus_03.png",
                "fresh/menu/egyptian/img_detail_egyptianhummus_04.png"
            ],
            "review_statics": {
                "review_count_postfix": "",
                "review_count": 0,
                "average_point": 0
            }
        },
        "list_index": 11,
        "type": 7,
        "price": 45,
        "price_discount": 40.5,
        "price_discount_event": true,
        "price_unit": 0,
        "category": [],
        "status": 1,
        "sales_time": 3,
        "type_name": "Chop Salad",
        "type_index": 0,
        "status_label": "ORDER FOR DINNER",
        "badge": [
            {
                "color": "#aabbcc",
                "type": 0,
                "name": "GOD BEST"
            }
        ]
    }
    ```
    
* **Notes:**
    
    Authentication information is an option.