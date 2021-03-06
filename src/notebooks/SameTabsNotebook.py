__author__ = 'Anti'

from frames import ExtractionPlotTabs, TargetsTab, Frame, ExtractionTab
from notebooks import Notebook
import constants as c


class SameTabsNotebook(Notebook.Notebook):
    def __init__(self, parent, name, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, name, row, column, **kwargs)
        self.tab_count = -1
        # self.default_tab_count = 0
        self.last_tab = None
        self.widget.bind("<<NotebookTabChanged>>", self.tabChangedEvent)

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.plusTabClicked()
            self.tabDefaultValues(-1)

    def addInitialTabs(self):
        self.last_tab = self.addTab("+")
        self.plusTabClicked()

    def newTab(self, row, column, **kwargs):
        raise NotImplementedError("newTab not implemented!")

    def addTab(self, text):
        tab = self.newTab(0, 0, delete_tab=self.deleteTab)
        self.widget.add(tab.widget, text=text)
        return tab

    def tabDefaultValues(self, tab_index):
        self.widgets_list[tab_index].loadDefaultValue()

    def loadDefaultValue(self):
        for i in range(self.tab_count+1):
            self.tabDefaultValues(i)

    def save(self, file):
        file.write(str(self.tab_count)+"\n")
        Notebook.Notebook.save(self, file)

    def load(self, file):
        self.deleteAllTabs()
        tab_count = int(file.readline())
        for i in range(tab_count):
            self.plusTabClicked()
        Notebook.Notebook.load(self, file)

    def deleteAllTabs(self):
        if self.tab_count != 0:
            self.widget.select(1)
            while self.tab_count > 0:
                self.deleteTab()

    def deleteTab(self):
        current = self.widget.index("current")
        del self.widgets_list[current]
        self.tab_count -= 1
        if self.tab_count != -1:
            self.changeActiveTab(current)
        self.widget.forget(current)
        return current

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
        self.widget.tab(self.tab_count, text=self.tab_count+1)
        self.last_tab = self.addTab(c.PLUS_TAB)


class ExtractionNotebook(SameTabsNotebook):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, c.EXTRACTION_NOTEBOOK, row, column, **kwargs)
        self.addInitialTabs()

    def newTab(self, row, column, **kwargs):
        return ExtractionPlotTabs.ExtractionTab(self.widget, row, column, **kwargs)


class PlotNotebook(SameTabsNotebook):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, c.PLOT_NOTEBOOK, row, column, **kwargs)
        self.addInitialTabs()

    def newTab(self, row, column, **kwargs):
        return ExtractionPlotTabs.PlotTab(self.widget, row, column, **kwargs)


class TargetNotebook(SameTabsNotebook):
    def __init__(self, parent, row, column, targetAdded, targetRemoved, getMonitorFreq, **kwargs):
        SameTabsNotebook.__init__(self, parent, c.TARGETS_NOTEBOOK, row, column, **kwargs)
        self.getMonitorFreq = getMonitorFreq
        self.targetAdded = targetAdded
        self.targetRemoved = targetRemoved
        self.addInitialTabs()

    def changeFreq(self):
        for widget in self.widgets_list:
            widget.changeFreq()

    def plusTabClicked(self):
        self.targetAdded()
        SameTabsNotebook.plusTabClicked(self)

    def newTab(self, row, column, **kwargs):
        return TargetsTab.TargetsTab(self.widget, self.getMonitorFreq, **kwargs)

    def deleteTab(self):  # Updates OptionMenu in Test tab
        deleted_tab = SameTabsNotebook.deleteTab(self)
        self.targetRemoved(deleted_tab)
