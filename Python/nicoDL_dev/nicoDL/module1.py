    def OnToggleRecordKeys(self, evt):
        self.recordingKeys = not self.recordingKeys
        if self.recordingKeys:
            self.recordBtn.SetLabel('Recording')
            self.keyEvents = list()
            self.stopwatchKeys.Start()
            self.playbackKeysBtn.Disable()
            self.txt.Clear()
            self.txt.SetFocus()
        else:
            self.playbackKeysBtn.Enable()
            self.recordBtn.SetLabel('Record')
