import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter/foundation.dart';
import 'api_service.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  
  WebSocketService._internal();

  WebSocketChannel? _channel;
  final _updateController = StreamController<Map<String, dynamic>>.broadcast();
  
  Stream<Map<String, dynamic>> get updates => _updateController.stream;

  void connect() {
    if (_channel != null) return; // Already connected or connecting

    final uri = Uri.parse(ApiService.baseUrl);
    final wsScheme = uri.scheme == 'https' ? 'wss' : 'ws';
    final wsUrl = '$wsScheme://${uri.host}:${uri.port}/ws/updates/';
    
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _channel!.stream.listen(
        (message) {
          try {
            final data = jsonDecode(message);
            if (data['type'] == 'update') {
              _updateController.add(data);
            }
          } catch (e) {
            debugPrint('Error parsing websocket message: $e');
          }
        },
        onDone: () {
          debugPrint('WebSocket closed, attempting to reconnect...');
          _channel = null;
          Future.delayed(const Duration(seconds: 5), connect);
        },
        onError: (error) {
          debugPrint('WebSocket error: $error');
          _channel = null;
        },
      );
      debugPrint('WebSocket connected to $wsUrl');
    } catch (e) {
      debugPrint('Failed to connect to WebSocket: $e');
      _channel = null;
      Future.delayed(const Duration(seconds: 5), connect);
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }
}
