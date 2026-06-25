import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class AboutPage extends StatelessWidget {
  const AboutPage({super.key});

  Future<void> _launchURL(String urlString) async {
    final uri = Uri.parse(urlString);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  Widget _buildContactLink(IconData icon, String text, String url) {
    return TextButton.icon(
      onPressed: () => _launchURL(url),
      style: TextButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
      icon: Icon(icon, size: 18, color: Colors.blue),
      label: Text(
        text, 
        style: const TextStyle(
          fontSize: 16, 
          color: Colors.blue, 
          decoration: TextDecoration.underline,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 600),
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.shield, size: 80, color: Colors.blueAccent),
              const SizedBox(height: 16),
              const Text(
                'ShieldPay',
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                'Version 1.0.0',
                style: TextStyle(fontSize: 16, color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7)),
              ),
              const SizedBox(height: 32),
              const Text(
                'Licensed to:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'ZeroShield IT Solutions and Cyber Security',
                style: TextStyle(fontSize: 20, color: Colors.blueAccent, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 16),
              _buildContactLink(Icons.phone, '+961 70 255 489', 'tel:+96170255489'),
              _buildContactLink(Icons.email, 'support@zeroshieldit.com', 'mailto:support@zeroshieldit.com'),
              _buildContactLink(Icons.language, 'www.zeroshieldit.com', 'https://www.zeroshieldit.com'),
              const SizedBox(height: 32),
              const Divider(),
              const SizedBox(height: 16),
              const Text(
                'Terms of Use',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'This software is proprietary and confidential. Unauthorized copying, distribution, or reverse engineering is strictly prohibited. By using ShieldPay, you agree to the terms and conditions outlined in the end-user license agreement provided by ZeroShield IT Solutions.',
                textAlign: TextAlign.center,
                style: TextStyle(height: 1.5),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
