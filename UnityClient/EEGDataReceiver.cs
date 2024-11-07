using UnityEngine;
using System;
using System.Collections;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using TMPro;

public class EEGDataReceiver : MonoBehaviour
{
    //This script is compatible with the Macrotellect BrainlinkPro EEG Device 

    [Header("Display Settings")]
    public TextMeshProUGUI displayText; // Reference to TMP text component to display EEG values
    public bool displayValues = true; // Toggle for displaying values
    private ClientWebSocket websocket;
    private const string WebSocketURL = "ws://127.0.0.1:8000/eeg";
    private CancellationTokenSource cancellationTokenSource;
    private bool isConnected = false;

    // EEG data structure
    [System.Serializable]
    public class EEGData
    {
        public int Signal;
        public int Attention;
        public int Meditation;
        public int Delta;
        public int Theta;
        public int LowAlpha;
        public int HighAlpha;
        public int LowBeta;
        public int HighBeta;
        public int LowGamma;
        public int HighGamma;
    }

    public EEGData currentEEGData { get; private set; }
    public bool IsConnected => isConnected;

    private async void Start()
    {
        // Verify TMP text component is assigned
        if (displayText == null)
        {
            Debug.LogError("Please assign a TextMeshProUGUI component to the displayText variable!");
        }

        await ConnectToWebSocket();

        // Start the display update coroutine
        if (displayValues)
        {
            StartCoroutine(UpdateDisplayText());
        }
    }

    // Coroutine to update the display text
    private IEnumerator UpdateDisplayText()
    {
        while (true)
        {
            if (displayValues && displayText != null && currentEEGData != null)
            {
                displayText.text = $"EEG Values:\n" +
                    $"Signal: {GetSignal()}\n" +
                    $"Attention: {GetAttention()}\n" +
                    $"Meditation: {GetMeditation()}\n" +
                    $"Delta: {GetDelta()}\n" +
                    $"Theta: {GetTheta()}\n" +
                    $"Low Alpha: {GetLowAlpha()}\n" +
                    $"High Alpha: {GetHighAlpha()}\n" +
                    $"Low Beta: {GetLowBeta()}\n" +
                    $"High Beta: {GetHighBeta()}\n" +
                    $"Low Gamma: {GetLowGamma()}\n" +
                    $"High Gamma: {GetHighGamma()}\n" +
                    $"\nConnection Status: {(IsConnected ? "Connected" : "Disconnected")}";
            }
            else if (!displayValues && displayText != null)
            {
                displayText.text = ""; // Clear the text when display is disabled
            }

            yield return new WaitForSeconds(0.1f); // Update 10 times per second
        }
    }

    // Method to toggle display
    public void ToggleDisplay()
    {
        displayValues = !displayValues;
        if (!displayValues && displayText != null)
        {
            displayText.text = "";
        }
    }

    private async Task ConnectToWebSocket()
    {
        websocket = new ClientWebSocket();
        cancellationTokenSource = new CancellationTokenSource();

        try
        {
            await websocket.ConnectAsync(new Uri(WebSocketURL), cancellationTokenSource.Token);
            isConnected = true;
            Debug.Log("WebSocket Connected");
            StartCoroutine(ReceiveLoop());
        }
        catch (Exception e)
        {
            Debug.LogError($"WebSocket Connection Error: {e.Message}");
            StartCoroutine(ReconnectWithDelay());
        }
    }

    private IEnumerator ReceiveLoop()
    {
        byte[] buffer = new byte[1024];
        while (isConnected)
        {
            var segment = new ArraySegment<byte>(buffer);
            WebSocketReceiveResult result = null;
            Task<WebSocketReceiveResult> receiveTask = null;

            // Start receive operation
            try
            {
                receiveTask = websocket.ReceiveAsync(segment, cancellationTokenSource.Token);
            }
            catch (Exception e)
            {
                Debug.LogError($"WebSocket Receive Error: {e.Message}");
                isConnected = false;
                StartCoroutine(ReconnectWithDelay());
                yield break;
            }

            // Wait for completion outside try-catch
            while (!receiveTask.IsCompleted)
            {
                yield return null;
            }

            // Process the result
            try
            {
                result = receiveTask.Result;

                if (result.MessageType == WebSocketMessageType.Text)
                {
                    string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    try
                    {
                        currentEEGData = JsonConvert.DeserializeObject<EEGData>(message);
                    }
                    catch (JsonSerializationException e)
                    {
                        Debug.LogError($"Error deserializing JSON: {e.Message} - JSON String: {message}");
                        continue;
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Error processing message: {e.Message}");
                isConnected = false;
                StartCoroutine(ReconnectWithDelay());
                yield break;
            }

            yield return null;
        }
    }

    private IEnumerator ReconnectWithDelay()
    {
        yield return new WaitForSeconds(5f);
        if (!isConnected)
        {
            Debug.Log("Attempting to reconnect...");
            _ = ConnectToWebSocket();
        }
    }

    // Getter methods for all EEG values
    public float GetSignal() { return currentEEGData?.Signal ?? 0; }
    public float GetAttention() { return currentEEGData?.Attention ?? 0; }
    public float GetMeditation() { return currentEEGData?.Meditation ?? 0; }
    public float GetDelta() { return currentEEGData?.Delta ?? 0; }
    public float GetTheta() { return currentEEGData?.Theta ?? 0; }
    public float GetLowAlpha() { return currentEEGData?.LowAlpha ?? 0; }
    public float GetHighAlpha() { return currentEEGData?.HighAlpha ?? 0; }
    public float GetLowBeta() { return currentEEGData?.LowBeta ?? 0; }
    public float GetHighBeta() { return currentEEGData?.HighBeta ?? 0; }
    public float GetLowGamma() { return currentEEGData?.LowGamma ?? 0; }
    public float GetHighGamma() { return currentEEGData?.HighGamma ?? 0; }

    // Method to get all EEG data at once
    public EEGData GetFullEEGData()
    {
        return currentEEGData;
    }

    private async void OnDestroy()
    {
        if (websocket != null && isConnected)
        {
            cancellationTokenSource.Cancel();
            try
            {
                await websocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Application closing", CancellationToken.None);
            }
            catch (Exception e)
            {
                Debug.LogError($"Error closing websocket: {e.Message}");
            }
            websocket.Dispose();
        }
    }

    // Optional: Method to manually reconnect
    public async void Reconnect()
    {
        if (websocket != null)
        {
            await websocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Reconnecting", CancellationToken.None);
            websocket.Dispose();
        }
        await ConnectToWebSocket();
    }
}
