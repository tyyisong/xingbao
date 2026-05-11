"""
星宝 API 服务器 — 为前端提供对话、报告和历史记录接口
启动: python3 server.py
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

app = Flask(__name__)
CORS(app)

# 全局引擎实例（单用户MVP，后续可扩展为多用户session管理）
engine = DialogueEngine(child_name="宏伟", child_age=10)


@app.route('/api/chat', methods=['POST'])
def chat():
    """孩子发送消息，星宝回复"""
    data = request.get_json()
    child_input = data.get('message', '').strip()
    if not child_input:
        return jsonify({'error': '消息不能为空'}), 400

    reply = engine.chat(child_input)

    # 提取被标注的兴趣标签
    last_child_msg = None
    for turn in reversed(engine.child.dialogue_history):
        if turn.role == 'child':
            last_child_msg = turn
            break

    tags = []
    if last_child_msg and last_child_msg.interest_tags:
        from config import INTEREST_DIMENSIONS
        tags = [
            {'dim': dim, 'label': INTEREST_DIMENSIONS.get(dim, {}).get('label', dim), 'score': s}
            for dim, s in last_child_msg.interest_tags.items() if s > 0
        ]
        tags.sort(key=lambda x: x['score'], reverse=True)

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
    return jsonify({
        'childName': engine.child.nickname,
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
    """获取聊天记录"""
    days = int(request.args.get('days', 7))
    history = []
    for turn in engine.child.dialogue_history:
        history.append({
            'timestamp': turn.timestamp.isoformat(),
            'role': turn.role,
            'content': turn.content,
            'tags': [
                {'dim': dim, 'score': score}
                for dim, score in (turn.interest_tags or {}).items() if score > 0
            ] if turn.interest_tags else [],
        })
    return jsonify({'history': history[-days * 20:]})  # 最近N天的对话


@app.route('/api/status', methods=['GET'])
def status():
    """获取星宝当前状态"""
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
    return jsonify({'status': 'ok', 'child': engine.child.nickname})


if __name__ == '__main__':
    print("🌟 星宝 API 服务启动中...")
    print("📍 http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
