**Product information**
----

* **URL**

    /v2/restaurant/<restaurant_id>/brand
    
* **Method:**

    `GET`

*  **URL Params**

   **Required:**

   `restaurant_id=[integer]`

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
    {
    "code": 200,
    "message": "success",
    "brand": {
        "id": 7,
        "restaurant_logo": "restaurant/viastelle/logo_brand_viastelle.png",
        "restaurant_region": "In Shanghai",
        "chef_name": "The GOD - ViaStelle",
        "chef_image": "restaurant/viastelle/img_brand_viastelle_1.png",
        "chef_content": {
            "chef_introduction": [
                {
                    "chef_name": "J. A. Choi",
                    "chef_careers": [
                        {
                            "award_type": 1,
                            "job_position": "'Chef de partie'",
                            "award_grade": 1,
                            "restaurant_name": "Mingles, Seoul (KOR)"
                        }
                    ]
                }
            ],
            "title": "R&D CHEFS",
            "color": "#ffffff"
        },
        "award_image": "restaurant/viastelle/img_brand_viastelle_2.png",
        "award_content": {
            "title": "R&D CHEFS",
            "award_info": [
                "RECIPENT OF\nONE MICHELIN STAR 2016 & 2017",
                "VOTED #3 BEST NEW RESTAURANT\nIN AMERICA 2016 - Bon Appetit",
                "LOUISA SMITH WINE DIRECTOR\nOF THE YEAR 2016\n - SAN FRANCISCO MAGAZINE",
                "AWARDED 3.5 STARS FROM THE\nSAN FRANCISCO CHRONICLE 2016"
            ],
            "award_info_with_icon": [
                {
                    "align": "left",
                    "award_type": 0,
                    "award_grade": 0,
                    "content": "Wolfgang's Steakhouse\nSeoul (Korea)\n'Excutive Chef'"
                }
            ],
            "type": 1,
            "color": "#ffffff"
        },
        "restaurant_content": [
            {
                "align": "right",
                "type": "text",
                "content": "Team ViaStelle는 서울 옛 왕궁인 경복궁역의 중심부에 위치한 Kolon Fashion Research Institute로 부터 시작되어 2016년 팀을 결성하여 약 2여 년의 역사를 간직한 곳이다. 경복궁역의 고급스러운 지역적 특성과 함께 컨템포러리 프렌치 아시안 퀴진, 친절하고 완벽한 음식과 서비스가 조화롭게 어우러진다."
            },
            {
                "align": "left",
                "type": "image_hd",
                "content": "restaurant/viastelle/img_brand_viastelle_7.png"
            }
        ]
    },
    "products": [
        {
            "id": 148,
            "hub": 1,
            "menu": {
                "id": 76,
                "restaurant": {
                    "id": 7,
                    "name": "Via Stelle",
                    "chef": "Hawa Song, Jiae Choi",
                    "introduce_image": "restaurant/viastelle/img_chef_viastelle.png",
                    "award_info": []
                },
                "name": "Easy Start 3 Days Plan",
                "cooking_materials": "Balanced with light ingredients and vital nutrition",
                "image_main": "fresh/sub/img_smart_diet_3_days_plan_detail_eng.jpg",
                "image_detail": "fresh/sub/img_smart_diet_3_days_plan_detail_eng.jpg",
                "image_sub": "fresh/sub/img_smart_diet_3_days_plan_detail_eng.jpg",
                "image_thumbnail": "fresh/sub/img_thumnail_easy_start_3_days_plan_eng.jpg",
                "description": [
                    "3 days with healthy and diet friendly salads. Even when on a diet, don’t miss out on the nutrition and taste."
                ],
                "image_package": "",
                "prep_tips": {},
                "prep_plating_thumbnail": "",
                "prep_plating_url": "",
                "ingredients": [],
                "nutrition": [],
                "notices": [
                    "\"Delivery starts from next Monday\"",
                    "Plan your next week’s salads ahead with our themed suggestions. ",
                    "Subscribe to a plan, get your salad delivered on a set date & time, enjoy smart savings. "
                ],
                "subs_contents": [
                    {
                        "title": {
                            "text": "DAY 1 : Monday\nGuaca Hola / 644 Kcal",
                            "bold": true,
                            "underline": true
                        },
                        "content": [
                            "Salad that coms with shrimp seasoned with different kinds of herbs, added with Nacho chips to give an intense taste and a strong Mexican feel to it."
                        ]
                    }
                ],
                "media_contents": [
                    {
                        "media_title": {
                            "text": "CHOP SALAD IN ACTION",
                            "bold": true,
                            "underline": true
                        },
                        "media_content": [
                            {
                                "type": "video",
                                "content": "fresh/vid/chop_01.mp4",
                                "thumbnail": "fresh/vid/chop_01.png"
                            }
                        ],
                        "desc_title": {
                            "text": "",
                            "bold": false,
                            "underline": false
                        },
                        "description": [],
                        "section_title": []
                    }
                ],
                "image_detail_list": [
                    "fresh/sub/img_smart_diet_3_days_plan_detail_eng.jpg",
                    "fresh/menu/guaca/img_detail_guacahola_01.png"
                ],
                "review_statics": {
                    "review_count": 0,
                    "review_count_postfix": "",
                    "average_point": 0
                }
            },
            "list_index": 0,
            "type": 8,
            "price": 135,
            "price_discount": 127,
            "price_discount_event": true,
            "price_unit": 0,
            "category": [],
            "status": 1,
            "sales_time": 2,
            "type_name": "Subscription",
            "type_index": 1,
            "status_label": "ORDER FOR LUNCH",
            "badge": []
        }
    ]
}
    ```
    
* **Notes:**
    
    Authentication information is an option.