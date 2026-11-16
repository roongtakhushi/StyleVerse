import asyncio
import sys
import os
import httpx

sys.path.insert(0, os.path.abspath('backend'))
sys.path.insert(0, os.path.abspath('.'))
from app.main import app
from app.database import connect_to_mongo, close_mongo_connection, db_instance

async def run_ml_pipeline_tests():
    await connect_to_mongo()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
        print('=================================================================')
        print('           STYLEVERSE ML PIPELINE VERIFICATION SUITE             ')
        print('=================================================================')

        # -------------------------------------------------------------
        # STEP 1: AUTHENTICATION & MULTI-TENANT USER SETUP
        # -------------------------------------------------------------
        print('\n[1] SETUP USERS & TEST ACCOUNTS')
        user_main_email = 'fashion_user_prime@styleverse.com'
        user_secondary_email = 'fashion_user_secondary@styleverse.com'
        await db_instance.db.users.delete_many({'email': {'$in': [user_main_email, user_secondary_email]}})
        
        reg_1 = await client.post('/api/auth/register', json={
            'name': 'Primary Stylist',
            'email': user_main_email,
            'password': 'password123',
            'gender_preference': 'unisex'
        })
        assert reg_1.status_code == 200
        token_1 = reg_1.json()['access_token']
        headers_1 = {'Authorization': f'Bearer {token_1}'}
        user_1_id = reg_1.json()['user']['id']
        print(f'-> Registered Primary User: {user_1_id} ({user_main_email})')

        reg_2 = await client.post('/api/auth/register', json={
            'name': 'Secondary User',
            'email': user_secondary_email,
            'password': 'password123',
            'gender_preference': 'unisex'
        })
        assert reg_2.status_code == 200
        token_2 = reg_2.json()['access_token']
        headers_2 = {'Authorization': f'Bearer {token_2}'}
        user_2_id = reg_2.json()['user']['id']
        print(f'-> Registered Secondary User: {user_2_id} ({user_secondary_email})')

        # -------------------------------------------------------------
        # STEP 2: MODULE 3 - SKIN ANALYSIS & UNDERTONE CONFIRMATION
        # -------------------------------------------------------------
        print('\n[2] MODULE 3: SKIN ANALYSIS (CIELAB & PALETTES)')
        with open('backend/test_assets/real_samples/face_sample.jpg', 'rb') as f:
            skin_resp = await client.post('/api/skin/analyze', files={'file': ('face_sample.jpg', f, 'image/jpeg')}, headers=headers_1)
        assert skin_resp.status_code == 200, f'Skin error: {skin_resp.text}'
        skin_data = skin_resp.json()
        print('-> Extracted Skin Tone:', skin_data['estimated_skin_tone'])
        print('-> Estimated Undertone:', skin_data['estimated_undertone'])
        print('-> Perceptual Face HEX Sample:', skin_data['sample_hex'])
        print('-> Recommended Primary Palette:', skin_data['primary_palette'])
        assert len(skin_data['primary_palette']) >= 5, 'Palette list should be populated'

        # User confirms undertone
        confirm_resp = await client.put('/api/skin/confirm', json={
            'undertone': 'warm',
            'skin_tone': skin_data['estimated_skin_tone']
        }, headers=headers_1)
        assert confirm_resp.status_code == 200
        print('-> Confirmed undertone "warm" and updated palette')

        # Check GET /api/skin/palette
        pal_get = await client.get('/api/skin/palette', headers=headers_1)
        assert pal_get.status_code == 200
        print('-> GET /api/skin/palette returns', len(pal_get.json()['primary_palette']), 'colors')

        # -------------------------------------------------------------
        # STEP 3: EMPTY WARDROBE HANDLING TEST
        # -------------------------------------------------------------
        print('\n[3] EMPTY WARDROBE HANDLING VERIFICATION')
        await db_instance.db.wardrobe_items.delete_many({'user_id': user_1_id})
        empty_rec = await client.post('/api/outfits/generate', json={'occasion': 'casual'}, headers=headers_1)
        print('-> Empty wardrobe generate response: HTTP', empty_rec.status_code)
        assert empty_rec.status_code == 400
        assert 'Insufficient wardrobe items' in empty_rec.json()['detail']
        print('-> Detail:', empty_rec.json()['detail'])

        # -------------------------------------------------------------
        # STEP 4: MODULES 1 & 2 - CLOTHING UPLOAD, CLASSIFICATION, K-MEANS
        # -------------------------------------------------------------
        print('\n[4] MODULES 1 & 2: CLOTHING UPLOAD & ATTRIBUTE EXTRACTION')
        
        # 4a. Upload Top (Shirt)
        with open('backend/test_assets/real_samples/shirt_sample.jpg', 'rb') as f:
            shirt_resp = await client.post('/api/wardrobe/upload', files={'file': ('shirt_sample.jpg', f, 'image/jpeg')}, headers=headers_1)
        assert shirt_resp.status_code == 200
        shirt_doc = shirt_resp.json()
        print('-> Uploaded Top: ID=', shirt_doc['id'], 'Category=', shirt_doc['category'], 'Confidence=', shirt_doc['confidence'], 'Colors=', shirt_doc['dominant_colors'])
        assert shirt_doc['category'] == 'top'
        assert len(shirt_doc['dominant_colors']) == 3

        # 4b. Upload Bottom (Trousers)
        with open('backend/test_assets/real_samples/trousers_sample.jpg', 'rb') as f:
            trouser_resp = await client.post('/api/wardrobe/upload', files={'file': ('trousers_sample.jpg', f, 'image/jpeg')}, headers=headers_1)
        assert trouser_resp.status_code == 200
        trouser_doc = trouser_resp.json()
        print('-> Uploaded Bottom: ID=', trouser_doc['id'], 'Category=', trouser_doc['category'], 'Confidence=', trouser_doc['confidence'], 'Colors=', trouser_doc['dominant_colors'])
        assert trouser_doc['category'] == 'bottom'
        assert len(trouser_doc['dominant_colors']) == 3

        # 4c. Upload Footwear (Shoes)
        with open('backend/test_assets/real_samples/shoes_sample.jpg', 'rb') as f:
            shoes_resp = await client.post('/api/wardrobe/upload', files={'file': ('shoes_sample.jpg', f, 'image/jpeg')}, headers=headers_1)
        assert shoes_resp.status_code == 200
        shoes_doc = shoes_resp.json()
        print('-> Uploaded Footwear: ID=', shoes_doc['id'], 'Category=', shoes_doc['category'], 'Confidence=', shoes_doc['confidence'], 'Colors=', shoes_doc['dominant_colors'])
        assert shoes_doc['category'] == 'footwear'
        assert len(shoes_doc['dominant_colors']) == 3

        # Verify GET /api/wardrobe
        wardrobe_list = await client.get('/api/wardrobe', headers=headers_1)
        assert wardrobe_list.status_code == 200
        print('-> GET /api/wardrobe retrieved', len(wardrobe_list.json()), 'items for User 1')
        assert len(wardrobe_list.json()) == 3

        # -------------------------------------------------------------
        # STEP 5: USER OWNERSHIP & DATA ISOLATION TEST
        # -------------------------------------------------------------
        print('\n[5] USER OWNERSHIP & MULTI-TENANT ISOLATION CHECK')
        user2_wardrobe = await client.get('/api/wardrobe', headers=headers_2)
        print('-> User 2 sees', len(user2_wardrobe.json()), 'wardrobe items in their personal closet')
        assert len(user2_wardrobe.json()) == 0

        # User 2 attempts to access User 1's specific item directly
        item_id_1 = shirt_doc['id']
        cross_res = await client.get(f'/api/wardrobe/{item_id_1}', headers=headers_2)
        print('-> User 2 accessing User 1 item: HTTP', cross_res.status_code, cross_res.json())
        assert cross_res.status_code == 403

        # -------------------------------------------------------------
        # STEP 6: MODULE 4 - HYBRID OUTFIT RECOMMENDATION ENGINE
        # -------------------------------------------------------------
        print('\n[6] MODULE 4: OUTFIT RECOMMENDATION (S = 0.35C + 0.25K + 0.20O + 0.10P + 0.10V)')
        rec_post = await client.post('/api/outfits/generate', json={
            'occasion': 'college',
            'style': 'casual',
            'use_wardrobe': True
        }, headers=headers_1)
        assert rec_post.status_code == 200
        rec_data = rec_post.json()
        print('-> Combinations Evaluated:', rec_data['total_combinations_evaluated'])
        print('-> Recommendations Generated:', len(rec_data['recommendations']))
        assert len(rec_data['recommendations']) > 0

        best_outfit = rec_data['recommendations'][0]
        print('-> Top Outfit ID:', best_outfit['id'])
        print('-> Compatibility Score S:', best_outfit['compatibility_score'], '/ 100')
        print('-> Normalized Breakdown:', best_outfit['metrics'])
        print('-> Generated Explanation:', best_outfit['explanation'])
        print('-> Matched Top:', best_outfit['items']['top']['subcategory'], best_outfit['items']['top']['dominant_colors'])
        print('-> Matched Bottom:', best_outfit['items']['bottom']['subcategory'], best_outfit['items']['bottom']['dominant_colors'])
        print('-> Matched Footwear:', best_outfit['items']['footwear']['subcategory'], best_outfit['items']['footwear']['dominant_colors'])

        # Test GET /api/outfits/recommended
        rec_get = await client.get('/api/outfits/recommended', headers=headers_1)
        assert rec_get.status_code == 200
        print('-> GET /api/outfits/recommended returned', len(rec_get.json()), 'persisted recommendations')
        assert len(rec_get.json()) > 0

        # -------------------------------------------------------------
        # STEP 7: MONGODB DATABASE VERIFICATION
        # -------------------------------------------------------------
        print('\n[7] VERIFY MONGODB PERSISTED RECORDS')
        mongo_users = await db_instance.db.users.count_documents({'email': user_main_email})
        mongo_profiles = await db_instance.db.style_profiles.count_documents({'user_id': user_1_id})
        mongo_items = await db_instance.db.wardrobe_items.count_documents({'user_id': user_1_id})
        mongo_recs = await db_instance.db.outfit_recommendations.count_documents({'user_id': user_1_id})
        print('-> MongoDB [users]:', mongo_users, 'record(s)')
        print('-> MongoDB [style_profiles]:', mongo_profiles, 'record(s)')
        print('-> MongoDB [wardrobe_items]:', mongo_items, 'record(s)')
        print('-> MongoDB [outfit_recommendations]:', mongo_recs, 'record(s)')
        assert mongo_users == 1 and mongo_profiles == 1 and mongo_items == 3 and mongo_recs >= 1

        print('\n=================================================================')
        print('    ALL 5 MODULES & TEST CRITERIA PASSED WITHOUT COMPROMISE!     ')
        print('=================================================================')

    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(run_ml_pipeline_tests())
