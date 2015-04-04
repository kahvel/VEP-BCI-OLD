__author__ = 'Anti'

from frames import ExtractionPlotTabs, TargetsTab, Frame
import ttk


class SameTabsNotebook(Frame.AbstractFrame):
    def __init__(self, parent, name, row, column, **kwargs):
        Frame.AbstractFrame.__init__(self, parent, name, row, column, **kwargs)
        self.tab_count = 0
        self.default_tab_count = 1
        self.last_tab = None
        self.create(ttk.Notebook(parent))
        self.widget.bind("<<NotebookTabChanged>>", self.tabChangedEvent)

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.plusTabClicked()

    def addInitialTabs(self):
        self.widgets_list.append(self.addTab("All"))
        self.last_tab = self.addTab("+")

    def newTab(self, row, column, **kwargs):
        raise NotImplementedError("newTab not implemented!")

    def addTab(self, text):
        tab = self.newTab(0, 0, delete_tab=self.deleteTab)
        #tab.create(self.widget)
        print(self.widget, tab.widget)
        self.widget.add(tab.widget, text=text)
        return tab

    def loadDefaultValue(self):
        self.widgets_list[0].loadDefaultValue()  # Default values to All tab
        for _ in range(self.default_tab_count):
            self.plusTabClicked()

    def save(self, file):
        file.write(str(self.tab_count)+"\n")
        Frame.Frame.save(self, file)

    def load(self, file):
        self.deleteAllTabs()
        tab_count = int(file.readline())
        for i in range(tab_count):
            self.plusTabClicked()
        Frame.Frame.load(self, file)

    def deleteAllTabs(self):
        if self.tab_count != 0:
            self.widget.select(1)
            while self.tab_count > 0:
                self.deleteTab()

    def deleteTab(self):
        current = self.widget.index("current")
        if current != 0:
            del self.widgets_list[current]
            self.tab_count -= 1
            self.changeActiveTab(current)
            self.widget.forget(current)

    def changeActiveTab(self, current):
        if current == self.tab_count+1:
            self.widget.select(current-1)
        else:
            while current < self.tab_count+2:
                self.widget.tab(current, text=self.widget.tab(current, "text")-1)
                current += 1

    def plusTabClicked(self):
        self.tab_count += 1
        self.widgets_list.append(self.last_tab)
        self.widgets_list[-1].loadDefaultValue()
        self.widget.tab(self.tab_count, text=self.tab_count)
        self.last_tab = self.addTab("+")


class ExtractionNotebook(SameTabsNotebook):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, "Extraction", row, column, **kwargs)
        self.addInitialTabs()

    def newTab(self, row, column, **kwargs):
        return ExtractionPlotTabs.ExtractionTab(self.widget, row, column, **kwargs)


class PlotNotebook(SameTabsNotebook):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, "Plot", row, column, **kwargs)
        self.addInitialTabs()

    def newTab(self, row, column, **kwargs):
        return ExtractionPlotTabs.PlotTab(self.widget, row, column, **kwargs)


class TargetNotebook(SameTabsNotebook):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, "Targets", row, column, **kwargs)
        self.validate_freq = kwargs["validate_freq"]
        self.addInitialTabs()

    def newTab(self, row, column, **kwargs):
        return TargetsTab.TargetsTab(self.widget, row, column, validate_freq=self.validate_freq, **kwargs)
