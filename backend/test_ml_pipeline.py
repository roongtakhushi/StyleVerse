import asyncio
import sys
import os
import httpx

sys.path.insert(0, os.path.abspath('backend'))
sys.path.insert(0, os.path.abspath('.'))
from app.main import app
from app.database import connect_to_mongo, close_mongo_connection, db_instance

async def run_end_to_end_ml_test():
    await connect_to_mongo()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
        print('=== 1. REGISTER AUTHENTICATED USER ===')
        email = 'ml_pipeline_tester@styleverse.com'
        await db_instance.db.users.delete_one({'email': email})
        reg_res = await client.post('/api/auth/register', json={
            'name': 'ML Pipeline Tester',
            'email': email,
            'password': 'securepassword123',
            'gender_preference': 'unisex'
        })
        assert reg_res.status_code == 200, f'Register failed: {reg_res.text}'
        token = reg_res.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        user_id = reg_res.json()['user']['id']
        print(f'User registered successfully with ID: {user_id}')
        
        print('\n=== 2. PRIORITY 2: SKIN ANALYSIS & UNDERTONE CONFIRMATION ===')
        with open('backend/test_assets/test_face.jpg', 'rb') as f:
            skin_res = await client.post('/api/skin/analyze', files={'file': ('test_face.jpg', f, 'image/jpeg')}, headers=headers)
        assert skin_res.status_code == 200, f'Skin analysis failed: {skin_res.text}'
        skin_data = skin_res.json()
        print('Estimated Skin Tone:', skin_data['estimated_skin_tone'])
        print('Estimated Undertone:', skin_data['estimated_undertone'])
        print('Sample Hex extracted:', skin_data['sample_hex'])
        print('Primary recommended palette:', skin_data['primary_palette'])
        
        # Confirm undertone manually
        conf_res = await client.put('/api/skin/confirm', json={
            'undertone': 'warm',
            'skin_tone': skin_data['estimated_skin_tone']
        }, headers=headers)
        assert conf_res.status_code == 200
        print('Undertone manually confirmed: warm')
        
        # Verify MongoDB style_profiles updated
        profile_in_db = await db_instance.db.style_profiles.find_one({'user_id': user_id})
        assert profile_in_db['undertone_confirmed'] is True
        print('Verified style_profiles in MongoDB: confirmed=True, palette count=', len(profile_in_db['colour_palette']))
        
        print('\n=== 3. PRIORITY 1: CLOTHING UPLOAD, K-MEANS COLOR EXTRACTION & CLASSIFICATION ===')
        await db_instance.db.wardrobe_items.delete_many({'user_id': user_id})
        
        # Upload Top
        with open('backend/test_assets/test_top.jpg', 'rb') as f:
            top_res = await client.post('/api/wardrobe/upload', files={'file': ('test_top.jpg', f, 'image/jpeg')}, headers=headers)
        assert top_res.status_code == 200, f'Top upload failed: {top_res.text}'
        top_data = top_res.json()
        print('Top Item ID:', top_data['id'], 'Category:', top_data['category'], 'Dominant Colors:', top_data['dominant_colors'])
        
        # Upload Bottom
        with open('backend/test_assets/test_bottom.jpg', 'rb') as f:
            bot_res = await client.post('/api/wardrobe/upload', files={'file': ('test_bottom.jpg', f, 'image/jpeg')}, headers=headers)
        assert bot_res.status_code == 200, f'Bottom upload failed: {bot_res.text}'
        bot_data = bot_res.json()
        print('Bottom Item ID:', bot_data['id'], 'Category:', bot_data['category'], 'Dominant Colors:', bot_data['dominant_colors'])
        
        # Upload Footwear
        with open('backend/test_assets/test_footwear.jpg', 'rb') as f:
            foot_res = await client.post('/api/wardrobe/upload', files={'file': ('test_footwear.jpg', f, 'image/jpeg')}, headers=headers)
        assert foot_res.status_code == 200, f'Footwear upload failed: {foot_res.text}'
        foot_data = foot_res.json()
        print('Footwear Item ID:', foot_data['id'], 'Category:', foot_data['category'], 'Dominant Colors:', foot_data['dominant_colors'])
        
        # Verify MongoDB storage
        db_items_count = await db_instance.db.wardrobe_items.count_documents({'user_id': user_id})
        print('Verified wardrobe items in MongoDB for this user:', db_items_count)
        assert db_items_count == 3
        
        print('\n=== 4. PRIORITY 3: OUTFIT RECOMMENDATION ENGINE ON ACTUAL WARDROBE ===')
        gen_res = await client.post('/api/outfits/generate', json={
            'occasion': 'college',
            'style': 'casual',
            'use_wardrobe': True
        }, headers=headers)
        assert gen_res.status_code == 200, f'Recommendation failed: {gen_res.text}'
        rec_data = gen_res.json()
        print('Total Combinations Evaluated:', rec_data['total_combinations_evaluated'])
        print('Top Recommendations Count:', len(rec_data['recommendations']))
        
        top_pick = rec_data['recommendations'][0]
        print('Best Match Compatibility Score:', top_pick['compatibility_score'], '/ 100')
        print('Score Breakdown Metrics:', top_pick['metrics'])
        print('Explanation:', top_pick['explanation'])
        print('Top item matched:', top_pick['items']['top']['id'], top_pick['items']['top']['dominant_colors'])
        print('Bottom item matched:', top_pick['items']['bottom']['id'], top_pick['items']['bottom']['dominant_colors'])
        print('Footwear matched:', top_pick['items']['footwear']['id'], top_pick['items']['footwear']['dominant_colors'])
        
        # Verify MongoDB outfit_recommendations collection
        recs_in_db = await db_instance.db.outfit_recommendations.count_documents({'user_id': user_id})
        print('Verified saved recommendations in MongoDB collection:', recs_in_db)
        assert recs_in_db > 0
        
        # Save to favorites
        save_res = await client.post('/api/outfits/save', json={
            'outfit_id': top_pick['id'],
            'occasion': 'college',
            'style': 'casual',
            'compatibility_score': top_pick['compatibility_score'],
            'explanation': top_pick['explanation'],
            'top_id': top_pick['items']['top']['id'],
            'bottom_id': top_pick['items']['bottom']['id'],
            'footwear_id': top_pick['items']['footwear']['id']
        }, headers=headers)
        assert save_res.status_code == 200
        print('Saved to favourites verified.')
        
        # Schedule in weekly planner
        plan_res = await client.post('/api/planner', json={
            'date': '2026-11-12',
            'occasion': 'college',
            'outfit_id': top_pick['id']
        }, headers=headers)
        assert plan_res.status_code == 200
        print('Weekly planner scheduling verified.')
        
        print('\n=== ALL PRIORITY 1, 2, 3, AND 4 ML INTEGRATION TESTS COMPLETED SUCCESSFULLY! ===')
        
    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(run_end_to_end_ml_test())

