"""
星宝 API 服务器 — 为前端提供对话、报告和历史记录接口
启动: DEEPSEEK_API_KEY="sk-xxx" python3 server.py
端口: 8080
"""
import json
import sys
import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))
from engine.dialogue import DialogueEngine
from engine.tagging import InterestAccumulator
from config import INTEREST_DIMENSIONS, EVOLUTION_BRANCHES
from services.feishu import append_row
from db import (
    init_db, create_child, get_child, get_star_baby_state, save_star_baby_state,
    save_dialogue, get_dialogue_history, save_evolution,
    get_interest_accumulation, save_interest_accumulation,
)

app = Flask(__name__)
CORS(app)

# 按 childId 缓存的引擎实例
_active_engines: dict[int, DialogueEngine] = {}


def _build_engine(child_id: int) -> DialogueEngine:
    """从数据库恢复或创建DialogueEngine"""
    child = get_child(child_id)
    if not child:
        raise ValueError(f"孩子不存在: {child_id}")

    engine = DialogueEngine(child_name=child["nickname"], child_age=child["age"])

    # 恢复星宝状态
    state = get_star_baby_state(child_id)
    engine.star_baby.level = state["level"]
    engine.star_baby.energy = state["energy"]
    engine.star_baby.current_branch = state["current_branch"]
    engine.star_baby.current_form = state["current_form"]
    engine.message_count = state["message_count"]
    engine.star_baby.total_dialogues = state["total_dialogues"]

    # 恢复兴趣累加器
    acc = get_interest_accumulation(child_id)
    for dim, info in acc.items():
        engine.accumulator.dimension_scores[dim] = info["total_score"]
        engine.accumulator.dimension_counts[dim] = info["hit_count"]
        if info["hit_count"] > 0:
            engine.accumulator.total_messages = max(
                engine.accumulator.total_messages, info["hit_count"]
            )

    return engine


def _get_engine(child_id: int) -> DialogueEngine:
    """获取缓存的引擎，不存在则从DB重建"""
    if child_id not in _active_engines:
        _active_engines[child_id] = _build_engine(child_id)
    return _active_engines[child_id]


def _persist_engine(child_id: int, engine: DialogueEngine):
    """将引擎状态持久化到数据库"""
    # 星宝状态
    save_star_baby_state(
        child_id=child_id,
        level=engine.star_baby.level,
        energy=engine.star_baby.energy,
        current_branch=engine.star_baby.current_branch,
        current_form=engine.star_baby.current_form,
        message_count=engine.message_count,
        total_dialogues=engine.star_baby.total_dialogues,
    )
    # 兴趣累加器
    save_interest_accumulation(
        child_id=child_id,
        dimension_scores=dict(engine.accumulator.dimension_scores),
        dimension_counts=dict(engine.accumulator.dimension_counts),
    )


# ═══════════════════════════════════════════
# API 端点
# ═══════════════════════════════════════════

@app.route('/api/onboarding', methods=['POST'])
def onboarding():
    """首次使用 — 创建孩子档案并初始化星宝"""
    data = request.get_json()
    nickname = data.get('nickname', '').strip()
    age = data.get('age', 8)

    if not nickname or len(nickname) < 1 or len(nickname) > 8:
        return jsonify({'error': '昵称需要1-8个字'}), 400
    if not isinstance(age, int) or age < 6 or age > 12:
        return jsonify({'error': '年龄需要在6-12岁之间'}), 400

    child_id = create_child(nickname, age)

    return jsonify({
        'childId': child_id,
        'nickname': nickname,
        'age': age,
        'starBaby': {
            'level': 1,
            'energy': 0,
            'energyMax': 50,
            'branch': None,
            'form': '初始形态',
        },
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """孩子发送消息，星宝回复"""
    data = request.get_json()
    child_input = data.get('message', '').strip()
    child_id = data.get('childId')

    if not child_input:
        return jsonify({'error': '消息不能为空'}), 400
    if not child_id:
        return jsonify({'error': '缺少 childId'}), 400

    try:
        engine = _get_engine(int(child_id))
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

    # 执行对话
    reply = engine.chat(child_input)

    # 提取本轮孩子消息的兴趣标签
    last_child_msg = None
    for turn in reversed(engine.child.dialogue_history):
        if turn.role == 'child':
            last_child_msg = turn
            break

    tags = []
    if last_child_msg and last_child_msg.interest_tags:
        tags = [
            {'dim': dim, 'label': INTEREST_DIMENSIONS.get(dim, {}).get('label', dim), 'score': s}
            for dim, s in last_child_msg.interest_tags.items() if s > 0
        ]
        tags.sort(key=lambda x: x['score'], reverse=True)

    # 持久化对话
    save_dialogue(int(child_id), 'child', child_input,
                  last_child_msg.interest_tags if last_child_msg else None)
    save_dialogue(int(child_id), 'star_baby', reply)

    # 持久化引擎状态
    _persist_engine(int(child_id), engine)

    # 记录进化事件
    if engine.star_baby.evolution_history:
        latest_evo = engine.star_baby.evolution_history[-1]
        save_evolution(
            child_id=int(child_id),
            from_level=latest_evo.from_level,
            to_level=latest_evo.to_level,
            branch=latest_evo.branch,
            message=latest_evo.message,
        )

    return jsonify({
        'reply': reply,
        'energy': engine.star_baby.energy,
        'energyMax': 50,
        'level': engine.star_baby.level,
        'branch': engine.star_baby.current_branch,
        'form': engine.star_baby.current_form,
        'tags': tags,
        'evolved': len(engine.star_baby.evolution_history) > 0,
    })


@app.route('/api/report', methods=['GET'])
def report():
    """获取家长端天赋报告"""
    child_id = request.args.get('childId', type=int)
    if not child_id:
        return jsonify({'error': '缺少 childId'}), 400

    try:
        engine = _get_engine(child_id)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

    child = get_child(child_id)

    return jsonify({
        'childName': child['nickname'],
        'totalInteractions': engine.child.get_total_interactions(),
        'level': engine.star_baby.level,
        'branch': engine.star_baby.current_branch,
        'form': engine.star_baby.current_form,
        'dominantDimension': engine.accumulator.get_dominant_dimension(),
        'radarData': engine.accumulator.get_radar_data(),
        'reportText': engine.get_parent_report(),
    })


@app.route('/api/history', methods=['GET'])
def history():
    """获取聊天记录（从数据库）"""
    child_id = request.args.get('childId', type=int)
    days = request.args.get('days', 7, type=int)
    if not child_id:
        return jsonify({'error': '缺少 childId'}), 400

    history_data = get_dialogue_history(child_id, days=days)
    return jsonify({'history': history_data})


@app.route('/api/status', methods=['GET'])
def status():
    """获取星宝当前状态"""
    child_id = request.args.get('childId', type=int)
    if not child_id:
        return jsonify({'error': '缺少 childId'}), 400

    try:
        engine = _get_engine(child_id)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

    return jsonify({
        'level': engine.star_baby.level,
        'energy': engine.star_baby.energy,
        'energyMax': 50,
        'branch': engine.star_baby.current_branch,
        'form': engine.star_baby.current_form,
        'dominantDimension': engine.accumulator.get_dominant_dimension(),
        'radarData': engine.accumulator.get_radar_data(),
    })


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})


@app.route('/', methods=['GET'])
def index():
    """落地页"""
    return app.send_static_file('hifi-mockup.html')


@app.route('/api/register', methods=['POST'])
def register():
    """报名表单提交 — 写入飞书表格"""
    data = request.get_json()
    if not data:
        return jsonify({'ok': False, 'error': '请填写完整信息'}), 400

    age = (data.get('age') or '').strip()
    city = (data.get('city') or '').strip()
    gender = (data.get('gender') or '').strip()
    phone = (data.get('phone') or '').strip()

    # 校验
    if not age:
        return jsonify({'ok': False, 'error': '请选择孩子年龄'}), 400
    if not city:
        return jsonify({'ok': False, 'error': '请填写所在城市'}), 400
    if gender not in ('boy', 'girl'):
        return jsonify({'ok': False, 'error': '请选择孩子性别'}), 400
    if not phone or len(phone) != 11 or not phone.isdigit():
        return jsonify({'ok': False, 'error': '请填写正确的11位手机号'}), 400

    gender_label = '男孩' if gender == 'boy' else '女孩'
    result = append_row(age, city, gender_label, phone)

    if result['ok']:
        return jsonify({'ok': True})
    else:
        return jsonify({'ok': False, 'error': result['error']}), 500


if __name__ == '__main__':
    print("🌟 星宝 API 服务启动中...")
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    try:
        init_db()
        print("📦 数据库已就绪")
    except Exception as e:
        print(f"⚠️ 数据库初始化跳过: {e}")
    print(f"📍 http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
