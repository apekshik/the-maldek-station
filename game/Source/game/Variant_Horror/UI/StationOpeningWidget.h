#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "StationOpeningWidget.generated.h"

UCLASS()
class GAME_API UStationOpeningWidget : public UUserWidget
{
 GENERATED_BODY()
public:
 float Elapsed=0,HintEnd=28;
 bool bToggled=false,bFocused=false;
protected:
 virtual int32 NativePaint(const FPaintArgs& Args,const FGeometry& Geometry,const FSlateRect& CullingRect,FSlateWindowElementList& Elements,int32 Layer,const FWidgetStyle& Style,bool bParentEnabled) const override;
};
